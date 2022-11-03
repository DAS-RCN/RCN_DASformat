"""
Read FEBUS HDF5 files
"""

import numpy as np
import h5py
import datetime
from pathlib import Path



#TODO: needs updating for export of IRIS header information
#TODO: needs better DOC-strings
#TODO: needs example file

def readFebus(fname):
    '''
    Takes a Febus HDF5 data file and returns a 2D numpy array containing the data and a simplified metadata dictionary.
    The output data array has shape nc x nt, where nc is the number of channels and nt the number of time samples.
    Note that this code assumes the standard Febus file format is used (i.e. with 50% overlapping block structure), if
    the format changes it will probably break the code.
    '''
    ACQ, HDR, Zones, duration, dstr = readFebusHeader(fname)
    HDF = h5py.File(fname, 'r')

    Host = list(HDF.keys())[0]
    tvec = HDF[Host]['Source1']['time']
    base = '/' + Host + '/Source1/' + Zones[0] + '/'
    DataSetName = list(HDF[base].keys())[0]
    cube = base + DataSetName

    shapea = HDF[cube].shape

    dataarray = np.zeros((shapea[2], shapea[1] // 2 * shapea[0]))

    for i in range(0, shapea[0], 1):
        dataarray[:, i * shapea[1] // 2:(i + 1) * shapea[1] // 2] = HDF[cube][i, shapea[1] // 4:3 * shapea[1] // 4, :].T

    metafebus = {'header':
                     {'dt': HDR['dt'],
                      'time': tvec[0] + shapea[1] // 4 * HDR['dt'],
                      'dx': HDR['dx'],}
                 }

    HDF.close()

    return dataarray, metafebus




def readFebusHeader(fn):
    """
    get the FEBUS storage header

    Parameters
    ----------
    fn : TYPE
        DESCRIPTION.

    Returns
    -------
    ACQ : TYPE
        DESCRIPTION.
    STORAGE : TYPE
        DESCRIPTION.
    Zones : TYPE
        DESCRIPTION.
    duration : TYPE
        DESCRIPTION.
    dstr : TYPE
        DESCRIPTION.

    """
    if not Path(fn).is_file():
        print("ERROR: File does not exist:")
        print('  ' + fn)
        ACQ, STORAGE, Zones, duration, dstr = []
        return ACQ, STORAGE, Zones, duration, dstr

    HDF  = h5py.File(fn, 'r')
    if not HDF:  # cancel button
        print("ERROR: Could not read file:" + fn)
        return

    Host     = list(HDF.keys())[0]
    tvec     = HDF[Host]['Source1']['time']
    dstr     = datetime.datetime.fromtimestamp(tvec[0]).strftime("%d %b %Y, %H:%M:%S")
    dt       = round(tvec[-1] - tvec[0])
    duration = datetime.timedelta(seconds=dt).__str__()
    # Aquisition settings
    SRC   = HDF.get('/' + Host + '/Source1')
    ACQ   = getHDF_header(SRC)
    ACQ['nBlox'] = len(tvec)
    Zones = list(SRC.keys())
    Zones.pop() # remove last entry, which is always the 'time' key
    STORAGE = []
    for z in Zones:
        STORAGE = getHDF_header(SRC[z])

    HDF.close()
    return ACQ, STORAGE, Zones, duration, dstr




def getHDF_header(obj):
    """
    get the FEBUS acquisition header

    Parameters
    ----------
    obj : TYPE
        DESCRIPTION.

    Returns
    -------
    HDR : TYPE
        DESCRIPTION.

    """
    HDR = {}
    for name, value in obj.attrs.items():
        #print(name + ":", value)
        if name == 'Extent':
            HDR["Extent"] = (value[0:4])
        elif name == 'WholeExtent':
            HDR["Extent"] = (value[0:4])
        elif name == 'PulseRateFreq':
            HDR["fSamp"] = value[0]/1000.
        elif name ==  'Spacing':
            HDR["dx"] = value[0]
            HDR["dt"] = value[1] /1000.
        elif name ==  'FiberLength':
            HDR["FiberLength"] = value[0]
        #else:
        #    HDR[name] = value
    return HDR
