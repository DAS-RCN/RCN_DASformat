# IRIS DAS data format

The IRIS DAS data format is a minimalistic approach to store data from Distributed Acoustic Sensing (DAS) recordings in an HDF5 file.


### Trace-Data
The signal is stored in as a **dataset** under root with the name ***traces***
Note that only strain or strainrate data are acceptable. Units are in strains or strains/sec, respectively.
Also note that data need to be geo-calibrated, such that excess fibre lengths (such as loops) are corrected for. 

```
traces          Traces of signal (nsmpl, nchnl), type=float32
```

### Header
Basic header information are stored as attributes under root. These are the very minimal data necessary to process the data.
```
DASFileVersion  Version of DAS file format, type=float16
domain          Data domain of signal traces (Strain, Strainrate, given in units of strains [m/m]) type=string
t0              UNIX time stamp of first sample in file type=float64
dt              Spacing between samples in seconds (i.e. inverse of the sampling rate) type=float32
GL              Gauge length [in meters] type=float32
lats            numpy array of latitudes (or y-values), type=float32
longs           numpy array of longitudes (or x-values), type=float32
elev            numpy array of elevations above sea-level (in meters), type=float32
```

### Meta-Data
Additional information can be stored under the name ***meta*** as dataset. This is free-format, but should be kept to a minimum.





### Filename convention
Files are stored in day-folders, each folder containing all files from this particular day. The file has the name syntax 
```
./2022-01-01/ProjName_YYYY-MM-DD_HH.MM.SS.FFF.das
```
where ***ProjName*** is a description of the project, or installation name
Note that files have the extension ***.das***, even though technically they are ***.hdf5*** files.

## Example File Information

```
>>> fname = './Reference_2022-09-28_09.00.00.000.das'
>>> infoDAS(fname, meta=True)

./Reference_2022-09-28_09.00.00.000.das
              traces == (10000, 300) numpy array
      DASFileVersion == 1.03
                  GL == 10.2
              domain == strainrate
                  dt == 0.001
                elev == (300,) numpy array
                lats == (300,) numpy array
               longs == (300,) numpy array
                  t0 == 2022-09-28 09:00:00
     /meta/dict/val1 == 1.23
     /meta/dict/val2 == dummy
        /meta/scalar == 3.14159265358979
        /meta/string == This is a test
        /meta/vector == (10,) numpy array
>>>
```


# Functions

```
def readDAS(fname):
```
```
def checkDASFileFormat(das):
```
```
def infoDAS(fname, meta=True):
```
```
def writeDAS(fname,  traces, domain, t0, dt, GL, lats, longs, elev, meta={}):
```
```
def compareDASdicts(das1, das2):
```
```
def make_dummy_data():
```

```
def basicASNreader(fname):
```






 




## Installation

TODO: Installation instructions are missing



## License
[MIT](https://choosealicense.com/licenses/mit/)
