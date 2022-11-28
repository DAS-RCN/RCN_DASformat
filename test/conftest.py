import io
from datetime import datetime

import numpy as np
import pytest

from miniDAS.format import Meta, miniDAS


def pytest_addoption(parser) -> None:
    parser.addoption("--plot", action="store_true", default=False)


@pytest.fixture(scope="session")
def plot(pytestconfig) -> bool:
    return pytestconfig.getoption("plot")


@pytest.fixture
def dummy_data(tmp_path) -> miniDAS:
    """
    Make some dummy data matrix and header value. This function can be used to
    generate data which may then be stored in a vendor-native format.
    """
    nchannels = 3000
    nsamples = 10000

    start_time = int(datetime.utcnow().timestamp() * 1e9)

    rstate = np.random.RandomState(123123)
    traces = rstate.randint(
        low=-10000, high=10000, size=(nchannels, nsamples), dtype=np.int32
    )

    lat0 = 48.858  # Eiffel Tower
    lon0 = 2.2945
    lats = np.linspace(lat0 - 0.1, lat0 + 0.1, nchannels)
    lons = np.full_like(lats, lon0)
    elevations = np.full_like(lats, 100.0)

    header = Meta(
        data_unit="cm/m",
        start_time_ns=start_time,
        strain_scale_factor=567890.1234,
        units_after_scaling="ue/s",
        channel_spacing_m=5.0,
        sampling_rate=1000.0,
        gauge_length=10.2,
        latitudes=lats,
        longitudes=lons,
        elevations=elevations,
    )
    return miniDAS.from_numpy(tmp_path / "test.hdf5", data=traces, meta=header)
