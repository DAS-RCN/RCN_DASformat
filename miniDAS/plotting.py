import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np


def ez_waterfall(
    data,  # data grid
    fsamp,  # temporal sampling rate of data in Hz
    t0=None,  # time of first sample, either Unix Timestamp or datetime64 object. If is None (default), relative times is assumed
    distances=None,
    show_decibel=True,
    climits=None,
    cmap="turbo",
    cb_label=None,
    title=None,
    time_format=None,
    time_ticks=range(0, 60, 15),
    dis_limits=None,
    dis_ticks=None,
    fig_size=(12, 6),
    ax=None,
):

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

    if distances is None:
        dis_units_str = "Channels"
        distances = [x for x in range(0, data.shape[1])]
    else:
        dis_units_str = "Distance along fibre"

    time_conversion_factor = 86400.0  # convert to mdate convention
    if time_format is None:
        t0 = None
        time_conversion_factor = 1.0
    elif time_format[-1].upper() == "S":
        locator = mdates.SecondLocator(bysecond=time_ticks)
        formater = mdates.DateFormatter(time_format)
    elif time_format[-1].upper() == "M":
        locator = mdates.MinuteLocator(byminute=time_ticks)
        formater = mdates.DateFormatter(time_format)
    elif time_format[-1].upper() == "H":
        locator = mdates.HourLocator(byhour=time_ticks)
        formater = mdates.DateFormatter(time_format)
    else:
        print(
            "ERROR using waterfall: Unknown option for time_format={}. Currently supported options are None, or format strings ending in S,M,or H".format(
                time_format
            )
        )
        return

    if isinstance(t0, np.uint64):
        t0 = t0 / time_conversion_factor / 1e9
    elif isinstance(t0, (float, int)):
        t0 = t0 / time_conversion_factor
    elif isinstance(t0, np.datetime64):
        t0 = (t0 / 1e9).astype(
            float
        ) / time_conversion_factor  # convert to mdate convention
    elif t0 is None:
        t0 = 0.0
    else:
        print(
            "ERROR using waterfall: invalid value for t0={}. valid data types are 'float (Unix Timestamp)', 'datetime64 object'".format(
                type(t0)
            )
        )
        return

    if show_decibel:
        data = 10 * np.log10(data)
        if cb_label is None:
            cb_label = "[dB]"
        else:
            cb_label = ""

    if climits is None:
        climits = [data.min(), data.max()]

    tvec = np.linspace(0, data.shape[0], data.shape[0])
    tvec = tvec / fsamp / time_conversion_factor + t0

    if ax is None:
        fig, ax = fig, ax = plt.subplots(1, 1, figsize=fig_size)
    hIm = ax.pcolormesh(
        distances, tvec, data, vmin=climits[0], vmax=climits[1], cmap=cmap
    )

    if title is not None:
        ax.set_title(title)

    if dis_limits is not None:
        ax.set_xlim(dis_limits[0], dis_limits[1])

    if dis_ticks is not None:
        ax.set_xticks(dis_ticks)

    if t0 != 0.0:
        datestr = (
            (t0 * time_conversion_factor)
            .astype("datetime64[s]")
            .item()
            .strftime("%d %b %Y")
        )
        ax.set_ylabel(datestr)

    cbar = ax.figure.colorbar(hIm, ax=ax, label=cb_label)

    ax.invert_yaxis()  # set time to go from top to bottom
    ax.set_xlabel(dis_units_str)
    if time_format is not None:
        ax.yaxis.set_major_locator(locator)
        ax.yaxis.set_major_formatter(formater)
    else:
        ax.set_ylabel("Time [sec]")

    return hIm, cbar, ax
