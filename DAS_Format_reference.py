# -*- coding: utf-8 -*-
"""
Reference reader and writer for Basic DAS file exchange format

03.11.2022
"""

import numpy as np
import h5py
from datetime import datetime, timezone
from sys import exit

"""
This file contains a set of functions to test data conversion to the IRIS RCN DAS format.
Consider this as a "reference-reader" to confirm your IRIS RCN DAS writer implementation

Suggested steps are
    1) Create some dummy data ("make_dummy_data()")
    2) Convert into a vendor native format (using some external code)
    3) Save as vendor native file
    4) Read vendor-file with the vendor-provided routines
    5) Export to IRIS DAS format with your implentation
    6) Read IRIS DAS format ("readDAS()")
    7) Print out file headers  ("infoDAS()")
    8) An automatic valitidy check can be perfomed (checkDASFileFormat()")
    9) You may also want to verify everything by comparing DAS data ("compareDASdicts(das1, das2)")

See at the bottom of this file for example usage
"""


version = 0.92




###############################################################
def make_dummy_data():
    """
    Make some dummy data matrix and header value. This function can be used to genrate data
    which may then be stored in a vendor-native format

    Args:
        No arguments for this function

    Retruns:
        das:  A dictionary with:
                - Dummy data matrix
                - Header information required by IRIS DAS
                - Examples of free-from meta data

    """
    nchnl = 300
    nsmpl = 10000
    start = '2022-09-28T09:00:00'

    t0    = np.datetime64(start, 'ns').astype('uint64')

    np.random.seed(int(t0/1e9))
    traces = np.random.rand(nsmpl, nchnl).astype('float32')

    Lat0  = 48.858222 #Eiffel Tower
    Long0 = 2.2945

    lats  = np.arange(Lat0, Lat0+.01, 0.01/nchnl)



    das = {}
    das['DASFileVersion'] = version
    das['domain'] = 'strainrate'
    das['t0']     = t0
    das['fsamp']  = 1000.
    das['GL']     = 10.2
    das['lats']   = lats
    das['longs']  = lats * 0 + Long0
    das['elev']   = lats * 0
    das['traces'] = traces
    das['meta']   = {}

    das['meta']['scalar'] = 3.14159265358979
    das['meta']['vector'] = np.arange(10, 20)
    das['meta']['string'] = 'This is a test'
    das['meta']['dict']   = {'val1':1.23, 'val2':'dummy'}
    return das




###############################################################
def _readDictInH5(trunk, group, dataset, show=False):
    """
    Helper function to read meta dataset from dataset. It is used in recursevely
    accessing a group folder structure in HDF% files

    Args:
        trunk:   The full trunk (path) to the current group
        group:   The name of the current group as part of the trunk
        dataset: The dataset to be recursively walked
        show:    Print out content (if True); mainly used in "infoDAS()" function

    Returns:
        dset:    The values contained in the current group dataset
    """
    if group =='':
        key = trunk
    else:
        key = trunk + '/' + group

    dset = {}
    if isinstance(dataset, h5py.Group): # test for group (go down)
        for grp in dataset.keys():
            dset[grp] = _readDictInH5(key, grp, dataset[grp], show=show)

    else:
        if isinstance(dataset, h5py.Dataset): # test for dataset
            if hasattr(dataset, "__len__"):
                dset = dataset[()]
            else:
                dset = dataset[:]

            if show:
                if isinstance(dset, str):
                    print("{:>20} == {}".format(key,dset))
                if isinstance(dset, bytes):
                    print("{:>20} == {}".format(key,dset.decode('UTF-8')))
                elif isinstance(dset, np.ndarray):

                    print("{:>20} == {} numpy array, ({:.5g} <= {} <={:.5g})".format(key,dset.shape, dset.min(), key, dset.max() ))
                elif isinstance(dset, list):
                    print("{:>20} == {} list".format(key,len(dset)))
                else:
                    print("{:>20} == {}".format(key,dset))

        else:
            print("{:>20} == {}".format(key, 'unknown contents'))
    return dset





###############################################################
def infoDAS(fname, meta=True):
    """
    Print header information of an IRIS DAS file
    """

    with h5py.File(fname, 'r') as fid:
        print('')
        print (fname)
        print("{:>20} == {} numpy array)".format('traces', fid['traces'].shape ))
        for k in fid.attrs.keys():
            val     = fid.attrs[k]
            if (k=='t0'):
                val = (val/1e3).astype('datetime64[us]')
                val = val.item().strftime('%d %b %Y %H:%M:%S.%f')


            if isinstance(val, str):
                print("{:>20} == {}".format(k,val))
            elif isinstance(val, np.ndarray):
                print("{:>20} == {} numpy array, ({:6.5g} <= {} <={:6.5g})".format(k,val.shape, val.min(), k, val.max() ))
            elif isinstance(val, list):
                print("{:>20} == {} list".format(k,len(val)))
            else:
                print("{:>20} == {}".format(k,val))

        if meta:
             _readDictInH5('', 'meta', fid['meta'], show=True)








###############################################################
def writeDAS(fname,  traces, domain, t0, fsamp, GL, lats, longs, elev, meta={}):
    """
    Write data in IRIS RCN DAS format
    Args:
        fname:  Filename of the file to be written
                Convention is "ProjectLabel_yyyy-mm-dd_HH.MM.SS.FFF.das"
                Leave empty to create filename automatically for storing in current working directory
        traces: DAS-signal data matrix, first dimension is "time", and second dimension "channel" (nSample, nChannel)
        domain: A string describing data domain; currently accepted are {"strain", "strainrate"}
        t0:     Unix time stamp of first sample (in nano-seconds)
        fsamp:  Samplin rate [in Hz]
        GL:     Gauge length [in meters]
        lats:   Vector of latitudes for each channel
        longs:  Vector of longitudes for each channel
        elev:   Vector of elevations for each channel [in meters]
        meta:   A dictionary of user-defined header values. Then is free-form

    Returns:
        Nothing
    """

    def _walkingDictStoring(trunk, group, dataset):
        if group =='':
            key = trunk
        else:
            key = trunk + '/' + group
        if isinstance(dataset, dict):
            group = fid.create_group(key) # user defined dictionary of additional header values, type=dict
            for grp in dataset.keys():
                 _walkingDictStoring(key, grp, dataset[grp])
        else:
            if isinstance(dataset, list):
                raise TypeError(f'Type \'LIST\' for field \'{key}\' is not supported in HDF5 format')
            fid.create_dataset(key, data=dataset)



    ##-----------------------------------
    if len(fname) == 0:
        #create filename from start time
        start     = (t0/1e6).astype('datetime64[ms]')
        start_str = start.item().strftime('%Y-%m-%d_%H.%M.%S.%f')[:-3]
        fname     = './Automatic_' + start_str + '.das'

    with h5py.File(fname, 'w') as fid:
        fid['traces']         = traces  # traces of signal (nsmpl, nchnl), type=float32

        fid.attrs['DASFileVersion'] = version    # Version of DAS file format, type=float16
        fid.attrs['domain']         = domain  # data domain of signal traces (Strain, Strainrate, given in units of strains [m/m]) type=string
        fid.attrs['t0']             = t0      # UNIX time stamp of first sample in file (in nano-seconds) type=uint64
        fid.attrs['fsamp']          = fsamp   # temporal sampling rate in Hz type=float32
        fid.attrs['GL']             = GL      # gauge length [in meters] type=float32
        fid.attrs['lats']           = lats    # numpy array of latitudes (or y-values), type=float32
        fid.attrs['longs']          = longs   # numpy array of longitudes (or x-values), type=float32
        fid.attrs['elev']           = elev    # numpy array of elevations above sea-level (in meters), type=float32

        #now walk the "meta" dictionary and store its values recursively
        _walkingDictStoring('meta', '', meta)
    return




###############################################################
def readDAS(fname):
    """
    Read IRIS DAS data

    Args:
        fname:  Filename to be read

    Returns:
        das:    A dictionary of signal data and header information
    """
    with h5py.File(fname, 'r') as fid:
        das = {}
        das['DASFileVersion']   = fid.attrs['DASFileVersion'][()]
        if das['DASFileVersion'] != version:
            print('Unknown DAS file version number!')
            exit()
        else:
            das['traces'] = fid['traces'][:]

            das['domain'] = fid.attrs['domain']
            das['t0']     = fid.attrs['t0']
            das['fsamp']  = fid.attrs['fsamp']
            das['GL']     = fid.attrs['GL']
            das['lats']   = fid.attrs['lats']
            das['longs']  = fid.attrs['longs']
            das['elev']   = fid.attrs['elev']
            das['meta']   = {}

        #now walk the "meta" dictionary and read its values recursively
        das['meta'] = _readDictInH5('', 'meta', fid['meta'])
    return das




###############################################################
def checkDASFileFormat(das):
    """
    Check the validity of an IRIS DAS file.

    Args:
        das:    Dictionary of signal data and header information
                (see readDAS())

    Return:
        valid:  A boolean of True/False depending on outcome of check
    """

    msg = ['ERROR:']
    valid = True

    if das['DASFileVersion'] != version:
       valid = False
       msg.append(f'DAS File Version is not {version}')


    if das['lats'].shape[0] != das['longs'].shape[0]:
       valid = False
       msg.append('lats and longs have diffrent lengths')

    if das['lats'].shape[0] != das['elev'].shape[0]:
       valid = False
       msg.append('lats and elev have diffrent lengths')



    if das['traces'].dtype != np.float32:
        valid = False
        msg.append('Traces seem to be stored as ' + das['traces'].dtype + ' but only float32 are allowed')

    if not das['domain'].upper() in ['STRAIN', 'STRAINRATE']:
        valid = False
        msg.append('Data seems to be in ' + das['domain'] + ' but only STRAIN or STRAINRATE data are acceptable')



    if not valid:
        [print (m) for m in msg]
    else:
        print('Everything seems ok! Great!')
    return valid




###############################################################
def compareDASdicts(das1, das2):
    """
    Compare two das-data dictionaries. Mainly used to check if any
    errors were introduduced during format conversions

    Args:
        das1:   Original DAS-data dictionary
        das2:   DAS-data dictionary to compare after conversions

    Return:
        valid:  A boolean of True/False depending on outcome of check
    """
    msg = ['ERROR:']
    valid = True


    if das1['DASFileVersion'] != das2['DASFileVersion']:
        valid = False
        msg.append('File Versions do not match')


    if np.min(abs(das1['traces'] - das2['traces'])) > 0.000:
        valid = False
        msg.append('Trace values don\'t match')

    if das1['domain'].upper() != das1['domain'].upper():
       valid = False
       msg.append('Data domain do not match ' + das2['domain'] )


    if das1['t0'] != das2['t0']:
        valid = False
        msg.append('T0 value doesn\'t match')


    if das1['fsamp'] != das2['fsamp']:
        valid = False
        msg.append('fsamp value doesn\'t match')

    if not np.array_equal(das1['longs'], das2['longs']):
        valid = False
        msg.append('longs value don\'t match')

    if not np.array_equal(das1['lats'], das2['lats']):
        valid = False
        msg.append('lats value don\'t match')

    if not np.array_equal(das1['elev'], das2['elev']):
        valid = False
        msg.append('elev value don\'t match')


    if not valid:
        [print (m) for m in msg]
    else:
        print('Everything seems ok! Great!')
    return valid





###############################################################
if __name__ == '__main__':
    #create dummy data
    das_dummy =  make_dummy_data()

    start     = (das_dummy['t0']/1e6).astype('datetime64[ms]')
    start_str = start.item().strftime('%Y-%m-%d_%H.%M.%S.%f')[:-3]
    fname     = './Reference_' + start_str + '.das'

    #write reference data file
    writeDAS(fname,  \
             das_dummy['traces'],\
             das_dummy['domain'],\
             das_dummy['t0'], \
             das_dummy['fsamp'], \
             das_dummy['GL'], \
             das_dummy['lats'], \
             das_dummy['longs'], \
             das_dummy['elev'], \
             meta=das_dummy['meta'])

    #read data
    infoDAS(fname, meta=True)
    das_out = readDAS(fname)


    #check = checkDASFileFormat(das_dummy)
    #check = checkDASFileFormat(das_out)
    #check = compareDASdicts(das_dummy, das_out)






