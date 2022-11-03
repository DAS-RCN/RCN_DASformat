# -*- coding: utf-8 -*-

import h5py
import numpy as np
import sys
sys.path.append("../../")

from DAS_Format_reference import writeDAS





def basicASNreader(fname):
    """
    Read ASN (vers 8) data files to be compatible wiht IRIS DAS format

    Args:
        fname (string): full file name

    Returns:

    """

    def _unwrap(phi, wrapStep=2*np.pi, axis=-1):
        """
        Unwrap phase phi by changing absolute jumps greater than wrapStep/2 to
        their wrapStep complement along the given axis. By default (if wrapStep is
        None) standard unwrapping is performed with wrapStep=2*np.pi.

        (Note: np.unwrap in the numpy package has an optional discont parameter
        which does not give an expected (or usefull) behavior when it deviates
        from default. Use this unwrap implementation instead of the numpy
        implementation if your signal is wrapped with discontinuities that deviate
        from 2*pi.)
        """
        scale = 2*np.pi / wrapStep
        return (np.unwrap(phi*scale, axis=axis)/scale).astype(phi.dtype)



    with h5py.File(fname, 'r') as fid:
        if fid['header']['dataType'][()] < 3:
                raise ValueError('Data seem to be not stored as time-differentiated phase data! Cannot proceed, sorry!')

        vers = fid['fileVersion'][()]
        if vers == 8:
            t0     = np.uint64(fid['header']['time'][()] * 1e9) #from unix time stamp as float in seconds to uint64 in nano-sec
            fsamp  = 1 / fid['header']['dt'][()]
            GL     = fid['header']['gaugeLength'][()]
            x      = fid['cableSpec']['sensorDistances'][:]

            #read raw data
            traces = fid['data'][:]

            #get scaling parameters
            scale = np.float32(fid['header']['dataScale'][()] / fid['header']['sensitivities'][0,0])

            traces = np.asfarray(traces, dtype=np.float32) * scale # scale phase data to be strain-rate
            traces = _unwrap(traces, fid['header']['spatialUnwrRange'][()], axis=1)
        else:
            return

    return traces, t0, fsamp, GL, x





if __name__ == '__main__':
    fname_ASN = r'./110740.hdf5'
    traces, t0, fsamp, GL, x = basicASNreader(fname_ASN)
    lats  = x
    longs = x * 0
    elev  = x * 0

    start     = (t0/1e6).astype('datetime64[ms]')
    start_str = start.item().strftime('%Y-%m-%d_%H.%M.%S.%f')[:-3]
    fname_DAS = './ASNexample' + start_str + '.das'
    writeDAS(fname_DAS,  traces, 'StrainRate', t0, fsamp, GL, lats, longs, elev, meta={})

