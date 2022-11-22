from datetime import datetime
from pprint import pprint

import numpy as np
import pytest

from miniDAS import Meta, miniDAS


def test_container(dummy_data: miniDAS):
    # The fixture is testing the minimal functionality already
    print(dummy_data.meta)


def test_meta():
    start_time = int(datetime.utcnow().timestamp() * 1e9)
    nchannels = 1000

    lat0 = 48.858  # Eiffel Tower
    lon0 = 2.2945
    lats = np.linspace(lat0 - 0.1, lat0 + 0.1, nchannels)
    lons = np.full_like(lats, lon0)
    elevations = np.full_like(lats, 100.0)

    with pytest.raises(AttributeError):
        Meta(
            data_unit="cm/m",
            start_time_ns=start_time,
            strain_scale_factor=567890.1234,
            units_after_scaling="ue/s",
            channel_spacing_m=5.0,
            sampling_rate=1000,
            gauge_length=10.2,
            latitudes=lats,
            longitudes=lons[:-1],
            elevations=elevations,
        )


def test_plot(dummy_data: miniDAS, plot: bool):
    if not plot:
        return
    dummy_data.plot()
