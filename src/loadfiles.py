import numpy as np
import pandas as pd
import argparse
from scipy.io import loadmat

################################################################################
# Functions to work with Shane Stone's s2 files
# s2 files have calculate densities differently than standard NGIMS L2 product.
# s2 files include temperatures/pressures from hydrostatic integration of dens
#
# Marek Slipski
# 20171016
# 20171115
################################################################################
species = ['Ar','CO2','N2']

def load_s2_data(filename):
    mat = loadmat(filename)
    mdata = mat['s2']
    ndata = {n: mdata[n][0, 0] for n in mdata.dtype.names}
    return ndata

def get_columns(s2_data):
    columns = [n for n, v in s2_data.iteritems()]
    return columns

def split_by_species(s2_data,columns):
    Ar_cols, N2_cols, CO2_cols,gen_cols = [],[],[],[]
    for c in columns:
        c_sp = c.split('_')[-1]
        if c_sp == species[0]:
            Ar_cols.append(c)
        elif c_sp == species[1]:
            CO2_cols.append(c)
        elif c_sp == species[2]:
            N2_cols.append(c)
        else:
            gen_cols.append(c)
    return {'Ar':Ar_cols,'N2':N2_cols,'CO2':CO2_cols,'misc':gen_cols}

def species_data_to_df(s2data,sp_cols):
    df = pd.DataFrame({s_c: s2data[s_c].flatten() for s_c in sp_cols})
    return df[[x+'_Ar' for x in ['alt','tmp','lon']]]

def sp_inbound_df(s2data,sp_cols):
    '''
    s2 files obtained from Shane at 2017 PSG have some columns that are
    full inbound and outbound and some only inbound. This does the same thing
    as species_data_to_df except reduces the data to just inbound.
    '''
    #do they have different lengths
    diff_lengths = np.unique(np.array([len(s2data[x]) for x in sp_cols]))

    #if only 1, should be just inboun already
    if len(diff_lengths)==1:
        df = speceis_data_to_df(s2data,sp_cols)

    # if 2 lengths, separate and rejoin
    elif len(diff_lengths)==2:
        c_a, c_b = [],[] #lists for different length columns
        for c in sp_cols: #loop through wanted cols, sort
            if len(s2data[c]) == diff_lengths[0]:
                c_a.append(c)
            elif len(s2data[c]) == diff_lengths[1]:
                c_b.append(c)
        df2a = pd.DataFrame({s_c: s2data[s_c].flatten() for s_c in c_a})
        df2b = pd.DataFrame({s_c: s2data[s_c].flatten() for s_c in c_b})
        df = pd.concat([df2a,df2b],axis=1,join='inner') # join, keep just inb

    # if more, there's a problem
    elif len(diff_lengths) > 2: #just in case extra length not due to inb/out
        print 'More than 2 different lengths of columns in s2 file (inb/out/?)'
        sys.exit()

    return df

def path_to_SpInDF(path,species,btrim=2.,ignore_topIC=True):
    '''
    Wrap all functions together to go from filename to temp DF.

    Useful because I'll likely only be using Ar Inbound Temps
    '''
    s2data = load_s2_data(path)
    cols = get_columns(s2data)
    split_cols = split_by_species(s2data,cols)
    sp_df = sp_inbound_df(s2data,split_cols[species])
    sp_df = sp_df[sp_df['alt_'+species]>sp_df['alt_'+species].min()+btrim]
    if ignore_topIC:
        top_temp = sp_df['tmp_'+species][sp_df['alt_'+species]==sp_df['alt_'+species].max()][0] #guessed alt
        sp_df = sp_df[sp_df['tmp_'+species] != top_temp] # temps not eqaul to guess
    sp_df['orbit'] = [s2data['orbit'].item()]*len(sp_df)
    sp_df['peri_lon'] = [sp_df['lon_'+species][sp_df['alt_'+species]==sp_df['alt_'+species].min()].item()]*len(sp_df)
    return sp_df

def combine(filelist):
    '''
    Generate dataframes for data from one or more files
    
    Inputs
    ------
    filelist: list, list of files to read
    
    Outputs
    -------
    data: DataFrame, all profiles
    '''
    data_pieces = []
    for f in filelist:
        try:
            ddf = path_to_SpInDF(f,'Ar')
        except IOError,e:
            print e
            continue
        data_pieces.append(ddf)
        
    data = pd.concat(data_pieces,ignore_index=True)
    return data

if __name__=='__main__':
    import sys
    with open(sys.argv[1],'rb') as infile:
        files = [x.rstrip() for x in infile.readlines()]
    print files[0]
    
    df = combine(files)
    print df.columns