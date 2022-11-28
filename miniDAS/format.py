from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from pprint import pformat
from typing import Literal

import h5py
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

DataUnit = Literal[
    "rad",
    "m/m",
    "cm/m",
    "mm/m",
    "um/m",
    "nm/m",
    "rad/2",
    "m/m/2",
    "cm/m/2",
    "mm/m/2",
    "um/m/2",
    "nm/m/2",
]
ScaledUnit = Literal["ue/s"]
_ALLOWED_DTYPES = (np.int16, np.int32, np.float32)

logger = logging.getLogger(__name__)


@dataclass
class Meta:
    data_unit: DataUnit
    start_time_ns: int
    sampling_rate: int
    channel_spacing_m: float
    gauge_length: float
    strain_scale_factor: float
    units_after_scaling: ScaledUnit
    latitudes: np.ndarray
    longitudes: np.ndarray
    elevations: np.ndarray
    end_time_ns: int = 0
    interrogator: str = ""

    @property
    def delta_t(self) -> float:
        """Sample spacing in seconds."""
        return 1.0 / self.sampling_rate

    @property
    def start_time(self) -> float:
        """Start time in seconds from UNIX epoch."""
        return self.start_time_ns / 1e9

    @property
    def end_time(self) -> float:
        """End time in seconds from UNIX epoch."""
        return self.end_time_ns / 1e9

    @property
    def start_date_time(self) -> datetime:
        """Start time as datetime object."""
        return datetime.fromtimestamp(self.start_time, tz=timezone.utc)

    @property
    def end_date_time(self) -> datetime:
        """End time as datetime object."""
        return datetime.fromtimestamp(self.end_time, tz=timezone.utc)

    def __str__(self) -> str:
        return pformat(self.__dict__)

    def __post_init__(self) -> None:
        if self.latitudes.size != self.longitudes.size != self.elevations.size:
            raise AttributeError(
                "Shape mismatch between latitudes, longitudes and elevation."
            )


class miniDAS:

    version: int = 1
    dataset: h5py.Dataset | np.ndarray
    _file: h5py.File
    filename: Path
    meta: Meta

    def __init__(self, dataset: h5py.Dataset, meta: Meta) -> None:
        self.dataset = dataset
        self._file = dataset.file

        meta.end_time_ns = int(meta.start_time_ns + meta.delta_t * 1e9 * self.n_samples)
        self.meta = meta

    @classmethod
    def from_numpy(
        cls,
        file: Path | str,
        data: np.ndarray,
        meta: Meta,
        compress: bool = True,
        force: bool = False,
    ) -> miniDAS:
        """Create a dataset from `np.array` and meta data.

        Args:
            file (Path | str): Filepath to write the HDF5 dataset to.
            data (np.ndarray): The DAS data in int16, int32 or float32 type.
            meta (Meta): Meta data describing the DAS data
            compress (bool, optional): Compress the HDF5 data with lzf compression.
                Defaults to True.
            force (bool, optional): Force overwrite the file if it exists.
                Defaults to False.

        Returns:
            miniDAS: The miniDAS container.
        """
        file = Path(file)
        if file.exists() and not force:
            raise OSError(f"{file} already exists, use force to overwrite")

        if data.dtype not in _ALLOWED_DTYPES:
            raise TypeError(f"Data has invalid dtype {data.dtype}")

        if meta.latitudes.size != data.shape[0]:
            raise AttributeError(
                "Missmatch between number of channels and"
                f"data shape {meta.latitudes.size} != {data.shape[0]}"
            )

        container = h5py.File(file, "w")
        logging.debug("Writing miniDAS to %s", file)
        dataset = container.create_dataset(
            "miniDAS",
            chunks=True,
            data=data,
            compression="lzf" if compress else False,
        )
        dataset.attrs["version"] = cls.version
        dataset.attrs.update(asdict(meta))

        return cls(dataset, meta)

    @classmethod
    def is_valid(cls, file: Path | str) -> bool:
        """Check if file is a miniDAS container.

        Args:
            file (Path | str): Path to file.

        Returns:
            bool: If the file is a miniDAS file.
        """
        file = Path(file)

        with h5py.File(file, "r") as container:
            dataset = container.get("miniDAS")
            if not dataset.attrs["version"] == cls.version:
                logger.warning(
                    f"file is version {dataset.attrs['version']},"
                    f" expected {cls.version}"
                )
                return False
        return True

    @classmethod
    def open(cls, file: Path | str) -> miniDAS:
        """Open a miniDAS file

        Args:
            file (Path | str): Path to file.

        Raises:
            AttributeError: When the file is not a miniDAS file.

        Returns:
            miniDAS: the container.
        """
        file = Path(file)
        if not cls.is_valid(file):
            raise AttributeError(f"{file} is not a miniDAS file.")

        container = h5py.File(file, "r")
        dataset = container.get("miniDAS")
        meta = dict(**dataset.attrs)
        meta.pop("version")

        return cls(dataset, Meta(**meta))

    def close(self) -> None:
        """Close the HDF5 file."""
        if self._file:
            self._file.close()

    def get_data(self) -> np.ndarray:
        """Get the data as `np.ndarray`

        Returns:
            np.ndarray: Data as `np.ndarray`
        """
        return self.dataset[()]

    def get_dataset(self) -> h5py.Dataset:
        """Get the HDF5 dataset.

        Returns:
            h5py.Dataset: The HDF5 dataset.
        """
        return self.dataset

    def plot(
        self,
        show_distance: bool = False,
        show_date_time: bool = True,
        cmap: str | None = None,
        figsize: tuple[float, float] | None = None,
        axes: plt.Axes | None = None,
        show_cbar: bool = True,
        interpolation: str = "antialiased",
    ) -> None | plt.Axes:
        """Plot the data

        Args:
            show_distance (bool, optional): Show distance in meter
                instead instead of channel number. Defaults to False.
            show_date_time (bool, optional): Show true date time instead of seconds.
                Defaults to True.
            cmap (str | None, optional): Matplotlib colormap name. Defaults to None.
            figsize (tuple[float, float] | None, optional): Size of the figure in inches.
                Defaults to None.
            axes (plt.Axes | None, optional): Plot into existing aces. Defaults to None.
            show_cbar (bool, optional): Show the colorbar, only works when `axes=None`.
                Defaults to True.
            interpolation (str, optional): Interpolation for imshow.
                Defaults to "antialiased".

        Returns:
            plt.Axes: The axes
        """
        if axes is None:
            fig = plt.figure(figsize=figsize)
            ax = fig.gca()
        else:
            fig = None
            ax = axes

        extent_lateral = (0, self.n_channels)
        if show_distance:
            extent_lateral = (0, self.n_channels * self.meta.channel_spacing_m)

        extent_time = (0.0, self.n_samples * self.meta.delta_t)
        if show_date_time:
            extent_time = (
                mdates.date2num(self.meta.start_date_time),
                mdates.date2num(self.meta.end_date_time),
            )

        data = self.get_data()
        img = ax.imshow(
            data,
            cmap=cmap,
            extent=(*extent_lateral, *extent_time),
            aspect="auto",
            interpolation=interpolation,
        )

        ax.invert_xaxis()
        ax.set_ylabel("Time [s]")

        if show_date_time:
            ax.set_ylabel("Time UTC")
            ax.yaxis_date()

        if show_cbar and fig is not None:
            fig.colorbar(img)

        if axes is None:
            plt.show()

        return ax

    @property
    def n_channels(self) -> int:
        """Number of channels in the container."""
        return self.dataset.shape[0]

    @property
    def n_samples(self) -> int:
        """Number of samples."""
        return self.dataset.shape[1]

    @property
    def duration(self) -> float:
        """Duration of the data set in seconds."""
        return self.n_samples * self.meta.delta_t
