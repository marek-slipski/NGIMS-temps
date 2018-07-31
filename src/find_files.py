import yaml
import datetime as dt
import glob
import os

## Get path to data from config file
with open('config.yaml') as cy:
    config = yaml.load(cy)
path_base = os.path.expanduser(config['data_path'])

# Basic filename structure
fn_base = 'mvn_ngi_s2_'
fn_end = 'csn.mat'

def str_dt(date_st):
    '''
    Convert str to datetime object
    '''
    if len(date_st) == 10:
        date_dt = dt.datetime.strptime(date_st,'%Y%m%d%H')
    elif len(date_st) == 8:
        date_dt = dt.datetime.strptime(date_st,'%Y%m%d')
    elif len(date_st) == 6:
        date_dt = dt.datetime.strptime(date_str,'%Y%m')
    elif len(date_st) == 4:
        date_dt = dt.datetime.strptime(date_str,'%Y')
    return date_dt

def files_from_date(date):
    fn_date = str(date)
    fn_tid = '[0-9]'*5
    fn_orb = '[0-9]'*5
    fn = fn_base+fn_date+'_'+fn_tid+'_'+fn_orb+'_'+fn_end
    match_files = glob.glob(path_base+fn)
    return match_files

def files_drange(start,end):
    '''
    Return list of file names between start date and end date
    Input
    -----
    start,end: str, start and end dates to parse
    
    Outputs
    ------
    files: list, paths to files between start and end
    '''
    new_dt = str_dt(start) #get dt objects of strings
    end_dt = str_dt(end)
    files = [] #initialize
    while new_dt < end_dt: #loop between
        new_files = files_from_date(new_dt.strftime('%Y%m%d')) #get file path
        files += new_files # add to list
        new_dt = new_dt + dt.timedelta(days=1) #update datetime
    return files

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Find MCS Files')
    parser.add_argument('dates',nargs=2,
                       help='Start and end dates to search between')
    
    
    
    args = parser.parse_args()
    start = args.dates[0]
    end = args.dates[1]
    
    files = files_drange(start,end)
    #print files
    for f in files:
        #print os.path.basename(f)
        print f
