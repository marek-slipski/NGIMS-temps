import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys

import loadfiles
import temp_fncs as tmp

class temp_info():
    '''
    Class to store information about temperature data
    from different databases to easily interact with.
    '''
    def __init__(self,database):
        '''
        Initialize class details
        
        Parameters
        ----------
        database: str ['MCS','NGIMS_s2','EUVM'], temperature database
        '''
        self.db = database
        self.cols = self.setup_cols()
        self.units = self.setup_units()
    
    def setup_cols(self):
        col_convers = {} # initialzie column name conversions
        if self.db == 'NGIMS_s2':
            col_convers['temp'] = 'tmp_Ar'
            col_convers['alt'] = 'alt_Ar'
            col_convers['lon'] = 'lon_Ar'
            col_convers['lst'] = 'ltm_Ar'
            col_convers['lat'] = 'lat_Ar'
            col_convers['Ls'] = 'lsubs_Ar'
            col_convers['sza'] = 'sza_Ar'
        return col_convers
    
    def setup_units(self):
        units = {}
        if self.db == 'NGIMS_s2':
            units['alt'] = 'km'
        return units
    
class plot_names():
    '''
    Class to store axis labels, etc.
    to avoid writing out in multiple scripts
    '''
    axis_labels = {}
    axis_labels['lon'] = r'Longitude ($^{\circ}$)'
    axis_labels['lst'] = 'Local Solar Time (hr/24)'
    axis_labels['lat'] = r'Latitude ($^{\circ}$)'
    axis_labels['Ls'] = r'$L_s$ ($^{\circ}$)'
    axis_labels['sza'] = r'Solar Zenith Angle ($^{\circ}$)'
    axis_labels['alt'] = 'Altitude [km]'
    axis_labels['pres'] = 'Pressure [Pa]'
    
    
    def __init__(x,y):
        '''
        Set instance parameters based on x and y
        '''
        self.x = x
        self.y = y
        self.setup()
        
    def setup(self):
        '''
        Set instance x and y lables and scales
        '''
        for ax in [self.x,self.y]:
            setattr(self,ax+'label',axis_labels[ax])
            if ax == 'pres':
                setattr(self,ax+scale,'log') # log if pressure
            else:
                setattr(self,ax+scale,'lin') # all others linear
                
class binning():
    '''
    Class for setting up bins and binning data
    '''
    def __init__(self,name,binsize):
        '''
        Parameters
        ----------
        num: int, number of bins
        '''
        self.name = name
        self.binsize = binsize
        self.binname = self.name+'_binmid'
        
    def get_bins(self,dmin,dmax):
        makebins = np.arange
        self.array = makebins(dmin,dmax,self.binsize)
        self.mids = (self.array[0:-1] + self.array[1:])/2
        
    
def add_bin_col(df,binin):
    return pd.cut(ddf[binin.name],binin.array,labels=binin.mids)

def make_agg_df(df,tempin,binins):
    # Calculate aggregates (means, stds, counts) in each bin
    cols = [b.binname for b in binins]
    Tname = tempin.cols['temp']
    if tempin.units['alt'] == 'km':
        altx = 1000
    else:
        altx = 1
    grouped = df.groupby(cols)
    binned_mean = grouped[Tname].mean() #temp 
    t_df = pd.DataFrame(binned_mean).reset_index().rename(columns={Tname:Tname+'_mean'})# Temperature
    t_df['alt_mean'] = grouped[tempin.cols['alt']].mean().values #alt for N2
    t_df['N2_mean'] =  tmp.wB_freq(t_df['alt_mean']*altx,t_df[Tname+'_mean']) #N2
    t_df[Tname+'_std'] = grouped[Tname].std().values
    t_df[Tname+'_count'] = grouped[Tname].count().values # counts

    print(t_df.head())
    return t_df

        
if __name__=='__main__':
    
    ## PARSE INPUTS
    #parser = loadfiles.data_input_args() # enter files/profiles/data in command line
    parser = argparse.ArgumentParser()
    parser.add_argument('files')
    plotparse = parser.add_argument_group('Plotting Arguments')
    # Plotting arguments
    plotparse.add_argument('-s','--save',action='store',
                           help='Save figure as')
    plotparse.add_argument('--hide',action='store_true',default=False,
                           help='Hide figure')
    plotparse.add_argument('-x','--xaxis',action='store',choices=['lat','lon','lst','Ls','sza'],
                           default='lon',
                           help='X-axis units')
    plotparse.add_argument('-y','--yaxis',action='store',choices=['alt','pres'],default='alt',
                           help='Y-axis units')
    plotparse.add_argument('--xbins',action='store',default=15,type=int,
                           help='Number of bins in x (default=16)')
    plotparse.add_argument('--ybins',action='store',default=5,type=float,
                           help='Number of bins in y [alt/pres] (default=50)')
    args = parser.parse_args() # get arguments

    
    
    
     ## LOAD DATA
    print '==loading data'
    with open(args.files,'r') as infile:
        files = [x.rstrip() for x in infile.readlines()]
    ddf = loadfiles.combine(files) # convert input data to DFs
    
    s2i = temp_info('NGIMS_s2')
    temp = s2i.cols['temp']
    x = s2i.cols[args.xaxis]
    y = s2i.cols[args.yaxis]
    
    ## SETUP BINS 
    print '==binning'
    # X-bins
    xbins = binning(x,args.xbins)
    ybins = binning(y,args.ybins)
    xbins.get_bins(ddf[x].min(),ddf[x].max())
    ybins.get_bins(ddf[y].min(),ddf[y].max())
    
    # Preprocess
    ddf.dropna(subset=[temp,x,y],inplace=True) # remove NaNs
    
    ddf[xbins.binname] = add_bin_col(ddf,xbins)
    ddf[ybins.binname] = add_bin_col(ddf,ybins)
    
    agg = make_agg_df(ddf,s2i,[xbins,ybins])