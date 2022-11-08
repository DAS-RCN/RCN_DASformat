"""
Read FEBUS HDF5 files
"""

import numpy as np
import h5py
import datetime
from pathlib import Path
import sys

sys.path.append("../../")

from DAS_Format_reference import writeDAS

#TODO: needs better DOC-strings


def basicFEBUSreader(fname):
    '''
    Takes a Febus HDF5 data file and returns a 2D numpy array containing the data and a simplified metadata dictionary.
    The output data array has shape nsmpl x nchnl,
    Note that this code assumes the standard Febus file format is used (i.e. with 50% overlapping block structure),
    '''
    HDF = h5py.File(fname, 'r')

    Host  = list(HDF.keys())[0]
    Zones = list(HDF.get('/' + Host + '/Source1').keys())
    Zones.remove('time')



    base = '/' + Host + '/Source1/' + Zones[0] + '/'
    DataSetName = list(HDF[base].keys())[0]
    cube = base + DataSetName

    shapea = HDF[cube].shape

    traces = np.zeros(( shapea[1] // 2 * shapea[0],shapea[2]))
    #read and concatenate all zones:
    for i in range(0, shapea[0], 1):
        traces[i * shapea[1] // 2:(i + 1) * shapea[1] // 2, :] = HDF[cube][i, shapea[1] // 4:3 * shapea[1] // 4, :]


    #get basic header information
    t0    = np.uint64(HDF[Host]['Source1']['time'][0] * 1e9)
    GL    = HDF[Host]['Source1']['Zone1'].attrs['GaugeLength']
    fsamp = 1000. / HDF[Host]['Source1']['Zone1'].attrs['Spacing'][1]

    #build the distance vector
    x = np.empty((0,))
    for zone in Zones:
        dx    = HDF[Host]['Source1'][zone].attrs['Spacing'][0]
        x0    = HDF[Host]['Source1'][zone].attrs['Extent'][0]
        x1    = HDF[Host]['Source1'][zone].attrs['Extent'][1]
        x     = np.concatenate((x, np.arange(x0,x1, dx)))



    HDF.close()
    return traces, t0, fsamp, GL, x




if __name__ == '__main__':
    fname_FEBUS = r'./Ham_2020-06-16T110728_UTC.h5'
    traces, t0, fsamp, GL, x = basicFEBUSreader(fname_FEBUS)
    lats  = x
    longs = x * 0
    elev  = x * 0

    start     = (t0/1e6).astype('datetime64[ms]')
    start_str = start.item().strftime('%Y-%m-%d_%H.%M.%S.%f')[:-3]
    fname_DAS = './FEBUSexample' + start_str + '.miniDAS'

    writeDAS(fname_DAS,  traces, 'nm/m/s', 1.,  'nm/m/s', t0, fsamp, GL, lats, longs, elev, meta={})
