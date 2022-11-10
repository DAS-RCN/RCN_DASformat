# -*- coding: utf-8 -*-
"""
Reference reader and writer for a minimalistic DAS file exchange format

03.11.2022
"""

import h5py
import numpy as np
from plotting import ez_waterfall

"""
This file contains a set of functions to test data conversion to the miniDAS format.
Consider this as a "reference-reader" to confirm your miniDAS writer implementation

Suggested steps are
    1) Create some dummy data ("make_dummy_data()")
    2) Convert into a vendor native format (using some external code)
    3) Save as vendor native file
    4) Read vendor-file with the vendor-provided routines
    5) Export to miniDAS format with your implentation
    6) Read miniDAS format ("readDAS()")
    7) Print out file headers  ("infoDAS()")

See at the bottom of this file for example usage
"""


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
                - Header information required by miniDAS
                - Examples of free-from meta data

    """
    nchnl = 300
    nsmpl = 10000
    start = "2022-09-28T09:00:00"

    start_time = np.datetime64(start, "ns").astype("uint64")

    np.random.seed(int(start_time / 1e9))
    traces = np.random.rand(nsmpl, nchnl).astype("float32")

    Lat0 = 48.858222  # Eiffel Tower
    Long0 = 2.2945

    lats = np.arange(Lat0, Lat0 + 0.01, 0.01 / nchnl)

    das = {}
    das["format"] = "miniDAS"
    das["version"] = version
    das["data_units"] = "rad"
    das["start_time"] = start_time
    das["scale_factor"] = 567890.1234
    das["units_after_scaling"] = "µε/s"
    das["sampling_rate"] = 1000.0
    das["gauge_length"] = 10.2
    das["latitudes"] = lats
    das["longitudes"] = lats * 0 + Long0
    das["elevations"] = lats * 0
    das["traces"] = traces
    das["meta"] = {}

    # some examples of user-defined header values
    das["meta"]["scalar"] = 3.14159265358979
    das["meta"]["vector"] = np.arange(10, 20)
    das["meta"]["string"] = "This is a test"
    das["meta"]["dict"] = {"val1": 1.23, "val2": "dummy"}
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
    if group == "":
        key = trunk
    else:
        key = trunk + "/" + group

    dset = {}
    if isinstance(dataset, h5py.Group):  # test for group (go down)
        for grp in dataset.keys():
            dset[grp] = _readDictInH5(key, grp, dataset[grp], show=show)

    else:
        if isinstance(dataset, h5py.Dataset):  # test for dataset
            if hasattr(dataset, "__len__"):
                dset = dataset[()]
            else:
                dset = dataset[:]

            if show:
                if isinstance(dset, str):
                    print("{:>20} == {}".format(key, dset))
                if isinstance(dset, bytes):
                    print("{:>20} == {}".format(key, dset.decode("UTF-8")))
                elif isinstance(dset, np.ndarray):

                    print(
                        "{:>20} == {} numpy array, ({:.5g} <= {} <={:.5g})".format(
                            key, dset.shape, dset.min(), key, dset.max()
                        )
                    )
                elif isinstance(dset, list):
                    print("{:>20} == {} list".format(key, len(dset)))
                else:
                    print("{:>20} == {}".format(key, dset))

        else:
            print("{:>20} == {}".format(key, "unknown contents"))
    return dset


###############################################################
def infoDAS(fname, meta=True):
    """
    Print header information of an miniDAS file
    """

    with h5py.File(fname, "r") as fid:
        print("")
        print(fname)

        if not fid.attrs.__contains__("format"):
            raise Exception("File does not seem to be a valid miniDAS file")

        print("{:>20} == {} numpy array".format("traces", fid["traces"].shape))
        for k in fid.attrs.keys():
            val = fid.attrs[k]
            if k == "start_time":
                val = (val / 1e3).astype("datetime64[us]")
                val = val.item().strftime("%d %b %Y %H:%M:%S.%f")
                print("{:>20} == {}".format(k, val))
            elif isinstance(val, str):
                print("{:>20} == '{}'".format(k, val))
            elif isinstance(val, np.ndarray):
                print(
                    "{:>20} == {} numpy array, ({:6.5g} <= {} <={:6.5g})".format(
                        k, val.shape, val.min(), k, val.max()
                    )
                )
            elif isinstance(val, list):
                print("{:>20} == {} list".format(k, len(val)))
            else:
                print("{:>20} == {}".format(k, val))

        if meta:
            _readDictInH5("", "meta", fid["meta"], show=True)


###############################################################
def writeDAS(
    fname,
    traces,
    data_units,
    scale_factor,
    units_after_scaling,
    start_time,
    sampling_rate,
    gauge_length,
    latitudes,
    longitudes,
    elevations,
    meta={},
):
    """
    Write data in miniDAS format
    Args:
        fname:  Filename of the file to be written
                Convention is "ProjectLabel_yyyy-mm-dd_HH.MM.SS.FFF.miniDAS"
                Leave empty to create filename automatically for storing in current working directory
        traces:               DAS-signal data matrix, first dimension is "time", and second dimension "channel" (nSample, nChannel)
        version:              Version of DAS file format, type=string
        data_units:           Units of the data-traces (e.g. radians, m/(m*s), m/m) type=string
        scale_factor:         A scaling factor to be multiplied with the data; type=float32
        units_after_scaling:  Units of traces after scaling is multiplied with traces; type=string
        start_time:           UNIX time stamp of first sample in file (in nano-seconds) type=uint64
        sampling_rate:        Temporal sampling rate in Hz type=float32
        gauge_length:         Gauge length [in meters] type=float32
        latitudes:            numpy array of latitudes (or y-values), type=float32
        longitudes:           numpy array of longitudes (or x-values), type=float32
        elevations:           numpy array of elevations above sea-level (in meters), type=float32
        meta:                 A dictionary of user-defined header values. Then is free-form

    Returns:
        Nothing
    """

    def _walkingDictStoring(trunk, group, dataset):
        if group == "":
            key = trunk
        else:
            key = trunk + "/" + group
        if isinstance(dataset, dict):
            group = fid.create_group(
                key
            )  # user defined dictionary of additional header values, type=dict
            for grp in dataset.keys():
                _walkingDictStoring(key, grp, dataset[grp])
        else:
            if isinstance(dataset, list):
                raise TypeError(
                    f"Type 'LIST' for field '{key}' is not supported in HDF5 format"
                )
            fid.create_dataset(key, data=dataset)

    ##-----------------------------------
    if len(fname) == 0:
        # create filename from start time
        start = (start_time / 1e6).astype("datetime64[ms]")
        start_str = start.item().strftime("%Y-%m-%d_%H.%M.%S.%f")[:-3]
        fname = "./Automatic_" + start_str + ".das"

    with h5py.File(fname, "w") as fid:
        fid[
            "traces"
        ] = traces  # traces of signal (nsmpl, nchnl), type=[float32 or int16]

        fid.attrs["format"] = "miniDAS"  # Format name, type=string
        fid.attrs["version"] = version  # Version of DAS file format, type=string
        fid.attrs[
            "data_units"
        ] = data_units  # units of the data-traces (e.g. radians, m/(m*s), m/m) type=string
        fid.attrs[
            "scale_factor"
        ] = scale_factor  # a scaling factor to be multiplied with the data; type=float32
        fid.attrs[
            "units_after_scaling"
        ] = units_after_scaling  # units of traces after scaling is multiplied with traces; type=string
        fid.attrs[
            "start_time"
        ] = start_time  # UNIX time stamp of first sample in file (in nano-seconds) type=uint64
        fid.attrs[
            "sampling_rate"
        ] = sampling_rate  # temporal sampling rate in Hz type=float32
        fid.attrs[
            "gauge_length"
        ] = gauge_length  # gauge length [in meters] type=float32
        fid.attrs[
            "latitudes"
        ] = latitudes  # numpy array of latitudes (or y-values), type=float32
        fid.attrs[
            "longitudes"
        ] = longitudes  # numpy array of longitudes (or x-values), type=float32
        fid.attrs[
            "elevations"
        ] = elevations  # numpy array of elevations above sea-level (in meters), type=float32

        # now walk the "meta" dictionary and store its values recursively
        _walkingDictStoring("meta", "", meta)
    return


###############################################################
def readDAS(fname, apply_scaling=True):
    """
    Read miniDAS data

    Args:
        fname:          Filename to be read
        apply_scaling:  if True, the scaling factor is applied to the data and output data are in "units_after_scaling"

    Returns:
        das:    A dictionary of signal data and header information
    """
    with h5py.File(fname, "r") as fid:
        if not fid.attrs.__contains__("format"):
            raise Exception("File does not seem to be a valid miniDAS file")

        das = {}
        das["format"] = fid.attrs["format"][:]
        if das["format"] != "miniDAS":
            raise Exception(
                "File does not seem to be a valid miniDAS file (format={})".format(
                    das["format"]
                )
            )
        das["version"] = fid.attrs["version"][:]
        if das["version"] != version:
            raise Exception(
                "Unknown DAS file version number: {}".format(das["version"])
            )

        das["traces"] = fid["traces"][:]
        das["data_units"] = fid.attrs["data_units"]
        das["scale_factor"] = fid.attrs["scale_factor"]
        das["units_after_scaling"] = fid.attrs["units_after_scaling"]

        das["start_time"] = fid.attrs["start_time"]
        das["sampling_rate"] = fid.attrs["sampling_rate"]
        das["gauge_length"] = fid.attrs["gauge_length"]
        das["latitudes"] = fid.attrs["latitudes"]
        das["longitudes"] = fid.attrs["longitudes"]
        das["elevations"] = fid.attrs["elevations"]
        das["meta"] = {}

        # now walk the "meta" dictionary and read its values recursively
        das["meta"] = _readDictInH5("", "meta", fid["meta"])

    if apply_scaling:
        das["traces"] = das["traces"] * das["scale_factor"]
        das["data_units"] = das["units_after_scaling"]
        das["scale_factor"] = 1.0

    return das


###############################################################
if __name__ == "__main__":
    # create dummy data
    das_dummy = make_dummy_data()

    ez_waterfall(
        das_dummy["traces"],
        fsamp=das_dummy["sampling_rate"],
        t0=das_dummy["start_time"],
        time_format="%H:%M:%S",
        time_ticks=range(0, 60, 2),
        title="Dummy data",
    )

    start = (das_dummy["start_time"] / 1e6).astype("datetime64[ms]")
    start_str = start.item().strftime("%Y-%m-%d_%H.%M.%S.%f")[:-3]
    fname = "./Reference_" + start_str + ".miniDAS"

    # write reference data file
    writeDAS(
        fname,
        das_dummy["traces"],
        das_dummy["data_units"],
        das_dummy["scale_factor"],
        das_dummy["units_after_scaling"],
        das_dummy["start_time"],
        das_dummy["sampling_rate"],
        das_dummy["gauge_length"],
        das_dummy["latitudes"],
        das_dummy["longitudes"],
        das_dummy["elevations"],
        meta=das_dummy["meta"],
    )

    # read data
    infoDAS(fname, meta=True)
    das_out = readDAS(fname)
