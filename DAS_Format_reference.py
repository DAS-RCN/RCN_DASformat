# -*- coding: utf-8 -*-
"""
Reference reader and writer for Basic DAS file exchange format

Version 1.0
28.09.2022
"""

import numpy as np
import h5py
from datetime import datetime, timezone
from sys import exit





###############################################################
def make_dummy_data():
    nchnl = 300
    nsmpl = 10000
    start = datetime.strptime('28 Sep 2022 09:00:00', '%d %b %Y %H:%M:%S').replace(tzinfo=timezone.utc)

    t0    = start.timestamp()

    np.random.seed(int(t0))
    traces = np.random.rand(nsmpl, nchnl).astype('float32')

    Lat0  = 48.858222 #Eiffel Tower
    Long0 = 2.2945

    lats  = np.arange(Lat0, Lat0+.01, 0.01/nchnl)



    das = {}
    das['DASFileVersion'] = 1.03
    das['domain'] = 'strainrate'
    das['t0']     = t0
    das['dt']     = 1/1000.
    das['GL']     = 10.2
    das['lats']   = lats
    das['longs']  = lats * 0 + Long0
    das['elev']   = lats * 0
    das['traces'] = traces
    das['meta']   = {}

    das['meta']['scalar'] = 3.14159265358979
    das['meta']['vector'] = np.arange(10, 20)
    das['meta']['string'] = 'This is a test'
    das['meta']['list']   = [1, 2, 'aaa', 'bbb']
    das['meta']['dict']   = {'val1':1.23, 'val2':'dummy'}
    return das




###############################################################
def _readDictInH5(base, group, data, show=False):
    if group =='':
        key = base
    else:
        key = base + '/' + group

    dset = {}
    if isinstance(data, h5py.Group): # test for group (go down)
        for grp in data.keys():
            dset[grp] = _readDictInH5(key, grp, data[grp], show=show)

    else:
        if isinstance(data, h5py.Dataset): # test for dataset
            if hasattr(data, "__len__"):
                dset = data[()]
            else:
                dset = data[:]

            if show:
                if isinstance(dset, str):
                    print("{:>20} == {}".format(key,dset))
                if isinstance(dset, bytes):
                    print("{:>20} == {}".format(key,dset.decode('UTF-8')))
                elif isinstance(dset, np.ndarray):
                    print("{:>20} == {} numpy array".format(key,dset.shape))
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
        print("{:>20} == {} numpy array".format('traces', fid['traces'].shape))
        for k in fid.attrs.keys():
            val     = fid.attrs[k]
            if (k=='t0'):
                val = datetime.utcfromtimestamp(val).isoformat(sep = ' ')

            if isinstance(val, str):
                print("{:>20} == {}".format(k,val))
            elif isinstance(val, np.ndarray):
                print("{:>20} == {} numpy array".format(k,val.shape))
            elif isinstance(val, list):
                print("{:>20} == {} list".format(k,len(val)))
            else:
                print("{:>20} == {}".format(k,val))

        if meta:
             _readDictInH5('', 'meta', fid['meta'], show=True)








###############################################################
def writeDAS(fname,  traces, domain, t0, dt, GL, lats, longs, elev, meta={}):              # dictionary of additional data, user-speicified

    def _storeDictInH5(base, group, data):
        if group =='':
            key = base
        else:
            key = base + '/' + group
        if isinstance(data, dict):
            group = fid.create_group(key) # user defined dictionary of additional header values, type=dict
            for grp in data.keys():
                 _storeDictInH5(key, grp, data[grp])

        else:
            if isinstance(data, list):
                raise TypeError(f'Type \'LIST\' for field \'{key}\' is not supported in HDF5 format')
            fid.create_dataset(key, data=data)



    with h5py.File(fname, 'w') as fid:
        #aGroup  = hdf5File.create_group("/A");
            fid['traces']         = traces  # traces of signal (nsmpl, nchnl), type=float32


            fid.attrs['DASFileVersion'] = 1.03    # Version of DAS file format, type=float16
            fid.attrs['domain']         = domain  # data domain of signal traces (Strain, Strainrate, given in units of strains [m/m]) type=string
            fid.attrs['t0']             = t0      # UNIX time stamp of first sample in file type=float64
            fid.attrs['dt']             = dt      # spacing between samples in seconds type=float32
            fid.attrs['GL']             = GL      # gauge length [in meters] type=float32
            fid.attrs['lats']           = lats    # numpy array of latitudes (or y-values), type=float32
            fid.attrs['longs']          = longs   # numpy array of longitudes (or x-values), type=float32
            fid.attrs['elev']           = elev    # numpy array of elevations above sea-level (in meters), type=float32

            #group = fid.create_group('meta') # user defined dictionary of additional header values, type=dict
            #for k, val in meta.items():
            _storeDictInH5('meta', '', meta)
    return




###############################################################
def readDAS(fname):

    with h5py.File(fname, 'r') as fid:
        das = {}
        das['DASFileVersion']   = fid.attrs['DASFileVersion'][()]
        if das['DASFileVersion'] != 1.03:
            print('Unknown DAS file version number!')
            exit()
        else:
            das['traces'] = fid['traces'][:]

            das['domain'] = fid.attrs['domain']
            das['t0']     = fid.attrs['t0']
            das['dt']     = fid.attrs['dt']
            das['GL']     = fid.attrs['GL']
            das['lats']   = fid.attrs['lats']
            das['longs']  = fid.attrs['longs']
            das['elev']   = fid.attrs['elev']
            das['meta']   = {}


        das['meta'] = _readDictInH5('', 'meta', fid['meta'])


    return das




###############################################################
def checkDASFileFormat(das):
    msg = ['ERROR:']
    check = True

    if das['DASFileVersion'] != 1.03:
       check = False
       msg.append('DAS File Version is not 1.03')


    if das['lats'].shape[0] != das['longs'].shape[0]:
       check = False
       msg.append('lats and longs have diffrent lengths')

    if das['lats'].shape[0] != das['elev'].shape[0]:
       check = False
       msg.append('lats and elev have diffrent lengths')



    if das['traces'].dtype != np.float32:
        check = False
        msg.append('Traces seem to be stored as ' + das['traces'].dtype + ' but only float32 are allowed')

    if not das['domain'].upper() in ['STRAIN', 'STRAINRATE']:
        check = False
        msg.append('Data seems to be in ' + das['domain'] + ' but only STRAIN or STRAINRATE data are acceptable')



    if not check:
        [print (m) for m in msg]
    else:
        print('Everything seems ok! Great!')
    return check




###############################################################
def compareDASdicts(das1, das2):
    msg = ['ERROR:']
    check = True


    if das1['DASFileVersion'] != das2['DASFileVersion']:
        check = False
        msg.append('File Versions do not match')


    if np.min(abs(das1['traces'] - das2['traces'])) > 0.000:
        check = False
        msg.append('Trace values don\'t match')

    if das1['domain'].upper() != das1['domain'].upper():
       check = False
       msg.append('Data domain do not match ' + das2['domain'] )


    if das1['t0'] != das2['t0']:
        check = False
        msg.append('T0 value doesn\'t match')


    if das1['dt'] != das2['dt']:
        check = False
        msg.append('dt value doesn\'t match')

    if not np.array_equal(das1['longs'], das2['longs']):
        check = False
        msg.append('longs value don\'t match')

    if not np.array_equal(das1['lats'], das2['lats']):
        check = False
        msg.append('lats value don\'t match')

    if not np.array_equal(das1['elev'], das2['elev']):
        check = False
        msg.append('elev value don\'t match')


    if not check:
        [print (m) for m in msg]
    else:
        print('Everything seems ok! Great!')
    return check





if __name__ == '__main__':
    #create dummy data
    das_dummy =  make_dummy_data()

    start     = datetime.utcfromtimestamp(das_dummy['t0'])
    start_str = start.strftime('%Y-%m-%d_%H.%M.%S.%f')
    fname     = './Reference_' + start_str[:-3] + '.das'

    #write reference data file
    writeDAS(fname,  \
             das_dummy['traces'],\
             das_dummy['domain'],\
             das_dummy['t0'], \
             das_dummy['dt'], \
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






