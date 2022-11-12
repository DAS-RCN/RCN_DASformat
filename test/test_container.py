from tempfile import NamedTemporaryFile

import numpy as np
import pytest

from miniDAS import miniDAS


def test_write(dummy_data: miniDAS):

    with NamedTemporaryFile() as f:
        with pytest.raises(OSError):
            dummy_data.write(f.name)

        dummy_data.write(f.name, force=True)
        f.flush()

        mdas = miniDAS.open(f.name)
        mdas.nsamples
        mdas.nchannels
        mdas.duration

        np.testing.assert_equal(mdas.get_data(), dummy_data.dataset)
        mdas.get_time_slice(dummy_data.meta.start_time_ns, dummy_data.meta.end_time_ns)
