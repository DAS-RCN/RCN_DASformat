# mini DAS data format

The miniDAS data format is a minimalistic approach to store data from Distributed Acoustic Sensing (DAS) recordings in an HDF5 file.

If you have any comments, please open an [issue on github](https://github.com/DAS-RCN/IRIS_DASformat/issues), or comment on existing ones.

### Filename convention
Files are stored in day-folders, each folder containing all files from this particular day. The file has the name syntax
```
./2022-01-01/ProjName_YYYY-MM-DD_HH.MM.SS.FFF.miniDAS
```
where ***ProjName*** is a description of the project, or installation name
Note that files have the extension ***.miniDAS***, even though technically they are ***.hdf5*** files.


### Trace-Data
The signal is stored in as a **dataset** under root with the name ***traces***
Units of the traces mus be given as a string in **data_unit** field. And additional **scale_factor** may be given that is to be multiplied with the trace data. This is accompanied by a string **units_after_scaling**
Note that data need to be geo-calibrated, such that excess fibre lengths (such as loops) are corrected for.

```
traces          Traces of signal (nsmpl, nchnl)
```

### Header
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




### Meta-Data
Additional information can be stored under the name ***meta*** as dataset. This is free-format, but should be kept to a minimum.





## Example File Information

```python
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


# Functions

### DAS_Format_reference.py
```python
def readDAS(fname, apply_scaling=True):
    """
    Read miniDAS data

    Args:
        fname:          Filename to be read
        apply_scaling:  if True, the scaling factor is applied to the data and output data are in "units_after_scaling"

    Returns:
        das:    A dictionary of signal data and header information
    """
```

```python
def infoDAS(fname, meta=True):
    """
    Print header information of an miniDAS file
    """
```
```python
def writeDAS(fname,  traces, data_units, scale_factor, units_after_scaling,\
             start_time, sampling_rate, gauge_length, \
             latitudes, longitudes, elevations, meta={}):
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

```

```python
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
```

### basicASNreader.py
```python
def basicASNreader(fname):
```


### plotting.py
```python
def ez_waterfall(...):
"""
Easy waterfall plotting, with plenty of convenience options notably a human-readable time axis

ARGUMENTS:
    data:         numpy array of shape (time, distance) of the data to be plotted
    dt:           temporal sample spacing of the data

    t0:           time of first time sample, either Unix Timestamp or datetime object.
                    If is None (default), relative time is assumed
    distances:    vector of distance along the fibre for each channel. If None (default), data is plotted as channels
    show_decibel: (bool) if True (default) data are converted to decibel
    climits:      two-element tuple of the color-limits.
                    Default is None, which automatically sets limits based on (min,max)
    cmap:         (string) Colormap of the plot
    cb_label:     (string) label of the colorbar
    title:        (string) title of the plot
    time_format:  (string) format string of the time ticks ticks. Options are:
                     None (default) uses time in seconds relative to first sample
                     Any valid string for datetime.strptime such as '%H:%M:%S' or '%H:%M'
    time_ticks:   (list of floats, range). position of time-ticks. Units correspond to the last letter of the time_format parameter
    dis_limits:   (two-element list of floats) set the distance limits
                  if None (default), shows all data
    dis_ticks:    (list, range) Position of the distance ticks
    ax:           (matplotlib axes object) Axes used to plot. Default is None, which generates a new figure and axes
    fig_size:     (two-element tuple of floats). If a new figure is created, the this determines size (in inches). Default is (12,6)



RETURNS:
    hIm:  matplotlib pcolormesh-object
    cbar: matplotlub colorbar-object
    ax:   maplotlib axes-object
"""
```











## Installation

TODO: Installation instructions are missing



## License
[MIT](https://choosealicense.com/licenses/mit/)
