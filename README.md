#DISCONTINOUED!!!!

** THIS PROJECT IS DISCONTINUED **
For the gloabl DAS month, native interrogator format is encouraged! More information about global DAS month 2023 can be found at
https://www.norsar.no/in-focus/global-das-monitoring-month-february-2023

A more comprehensive IRIS data format isunder development here: https://github.com/DAS-RCN/DAS_metadata





# miniDAS data format (discontinued)

The miniDAS data format is a minimalistic approach to store data from Distributed Acoustic Sensing (DAS) recordings in an HDF5 file.

## Filename convention

Files are stored in day-folders, each folder containing all files from this particular day. The file has the name syntax

```
./2022-01-01/ProjName_YYYY-MM-DD_HH.MM.SS.FFF.miniDAS
```

where ***ProjName*** is a description of the project, or installation name
Note that files have the extension ***.miniDAS***, even though technically they are ***.hdf5*** files.

## Trace-Data

The signal is stored in as a **dataset** under root with the name ***traces***
Units of the traces mus be given as a string in **data_unit** field. And additional **scale_factor** may be given that is to be multiplied with the trace data. This is accompanied by a string **units_after_scaling**
Note that data need to be geo-calibrated, such that excess fibre lengths (such as loops) are corrected for.

```
traces          Traces of signal (nsmpl, nchnl)
```

## Header

Basic header information are stored as attributes under root. These are the very minimal data necessary to process the data.

```
format                 Format name (must be 'miniDAS'), type=string
version                Version of DAS file format, type=string
data_units             Units of the data-traces (e.g. radians, m/(m*s), m/m) type=string
scale_factor           A scaling factor to be multiplied with the data; type=float32
units_after_scaling    Units of traces *after* scaling is multiplied with traces; type=string
start_time             UNIX time stamp of first sample in file (in nano-seconds) type=uint64
sampling_rate          Temporal sampling rate in Hz type=float32
gauge_length           Gauge length [in meters] type=float32
latitudes              numpy array of latitudes (or y-values), type=float32
longitudes             numpy array of longitudes (or x-values), type=float32
elevations             numpy array of elevations above sea-level (in meters), type=float32
meta                   Dictionary of addtional user-defined meta-data
```

### Additional Meta Data

Additional information can be stored under the name ***meta*** as dataset. This is free-format, but should be kept to a minimum.

## Example File Information

```py
>>> fname = './Reference_2022-09-28_09.00.00.000.miniDAS'
>>> infoDAS(fname, meta=True)

./Reference_2022-09-28_09.00.00.000.miniDAS
              traces == (10000, 300) numpy array
          data_units == 'rad'
          elevations == (300,) numpy array, (     0 <= elevations <=     0)
              format == 'miniDAS'
        gauge_length == 10.2
           latitudes == (300,) numpy array, (48.858 <= latitudes <=48.868)
          longitudes == (300,) numpy array, (2.2945 <= longitudes <=2.2945)
       sampling_rate == 1000.0
        scale_factor == 567890.1234
          start_time == 28 Sep 2022 09:00:00.000000
 units_after_scaling == 'µε/s'
             version == '0.1.0'

     /meta/dict/val1 == 1.23
     /meta/dict/val2 == dummy
        /meta/scalar == 3.14159265358979
        /meta/string == This is a test
        /meta/vector == (10,) numpy array, (10 <= /meta/vector <=19)
>>>
```

## Documentation

TBD

## Installation

### Using pip

Download miniDAS from pipy repositories using pip.

```bash
pip install miniDAS
```

### From source and for development

This method is recommended for development

```sh
git clone ...miniDAS
cd miniDAS
pip install -e .
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
