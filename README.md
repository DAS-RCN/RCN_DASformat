# IRIS DAS data format

The IRIS DAS data format is a minimalistic approach to store data from Distributed Acoustic Sensing (DAS) recordings in an HDF5 file.

If you have any comments, please open an [issue on github](https://github.com/DAS-RCN/IRIS_DASformat/issues), or comment on existing ones.

### Filename convention
Files are stored in day-folders, each folder containing all files from this particular day. The file has the name syntax 
```
./2022-01-01/ProjName_YYYY-MM-DD_HH.MM.SS.FFF.das
```
where ***ProjName*** is a description of the project, or installation name
Note that files have the extension ***.das***, even though technically they are ***.hdf5*** files.


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
meta            Dictionary of addtional user-defined meta-data
```
A few comments on the reasoning for the choices made here:
Generally, the idea is to make live easy for the analyst. Conversions are prone to error, and only the original data provider knows the correct way to do this
* data matrix (nsmpl/nchn) vs (nchn/nsmpl): depending on your programming language, either on is closer to the native matrix storage format for fastest way of processing (please open an "issue" if wrong)
* Strain/strain-rate is prefered to radians, as the former are units geophysists are used to. Please comment in the "Issues" section here about your thoughts on units. maybe nano-strain(rate) would be a more natural unit to use? Can we get away with float16?
* dt vs fsamp is a choice of taste and here dt was selected for no particular reason
* lat/long vs distance & dx: dx is the optical sensor spacing. This is actually of little use to a geophysicist. We are interested in actual sensor location. Imagine the case where you have a fibre loop of 50m in a cabinet somewhere (typical road monitoring example). Shared public data must(!!) be geo-calibrated. Users have no way to do tap tests. It is the data-providers responsibility to do that for the end-user. (At least for the global month, then the community can decide that this approach had it’s flaws…)
* elevation vs depth: This is also question of taste, and was decided on the IRIS seimometer convention of positive values are up.
* metric vs imperial units: Let's stick to the science convention most of the world is using





### Meta-Data
Additional information can be stored under the name ***meta*** as dataset. This is free-format, but should be kept to a minimum.





## Example File Information

```python
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

### DAS_Format_reference.py
```python
def readDAS(fname):
    """
    Read IRIS DAS data 
    
    Args:
        fname:  Filename to be read 
        
    Returns:
        das:    A dictionary of signal data and header information
    """
```
```python
def checkDASFileFormat(das):
    """
    Check the validity of an IRIS DAS file. 
    
    Args:
        das:    Dictionary of signal data and header information 
                (see readDAS())
    
    Return: 
        valid:  A boolean of True/False depending on outcome of check
    """
```
```python
def infoDAS(fname, meta=True):
    """
    Print header information of an IRIS DAS file
    """
```
```python
def writeDAS(fname,  traces, domain, t0, dt, GL, lats, longs, elev, meta={}):
    """
    Write data in IRIS RCN DAS format
    Args:
        fname:  Filename of the file to be written
                Convention is "ProjectLabel_yyyy-mm-dd_HH.MM.SS.FFF.das"
                Leave empty to create filename automatically for storing in current working directory
        traces: DAS-signal data matrix, first dimension is "time", and second dimension "channel" (nSample, nChannel)
        domain: A string describing data domain; currently accepted are {"strain", "strainrate"}
        t0:     Unix time stamp of first sample
        dt:     Sample spacing [in seconds]
        GL:     Gauge length [in meters]
        lats:   Vector of latitudes for each channel
        longs:  Vector of longitudes for each channel
        elev:   Vector of elevations for each channel [in meters]
        meta:   A dictionary of user-defined header values. Then is free-form
    
    Returns:
        Nothing
    """
```
```python
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
                - Header information required by IRIS DAS
                - Examples of free-from meta data
        
    """
```

### basicASNreader.py
```python
def basicASNreader(fname):
```






 




## Installation

TODO: Installation instructions are missing



## License
[MIT](https://choosealicense.com/licenses/mit/)
