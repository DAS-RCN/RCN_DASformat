from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import h5py
import numpy as np

DataUnit = Literal["m/m", "cm/m", "mm/m"]
ScaledUnit = Literal["ue/m"]


class OutOfBoundsError(BaseException):
    ...


@dataclass
class Meta:
    data_unit: DataUnit
    start_time_ns: int
    scale_factor: float
    units_after_scaling: ScaledUnit
    sampling_rate: int
    gauge_length: float
    latitudes: list[float]
    longitudes: list[float]
    elevations: list[float]
    end_time_ns: int = 0

    @property
    def deltat(self) -> float:
        return 1.0 / self.sampling_rate

    @property
    def start_time(self) -> float:
        return self.start_time_ns / 1e9

    @property
    def end_time(self) -> float:
        return self.end_time_ns / 1e9


class miniDAS:
    _file: h5py.File | None

    version: int = 1
    dataset: h5py.Dataset | np.ndarray
    meta: Meta

    def __init__(self, dataset: h5py.Dataset | np.ndarray, meta: Meta):
        self.dataset = dataset
        self._file = None

        if len(meta.latitudes) != len(meta.longitudes) != len(meta.elevations):
            raise AttributeError(
                "Shape mismatch between latitudes, longitudes and elevation."
            )
        if len(meta.latitudes) != self.nchannels:
            raise AttributeError("Missmatch between number of channels and data shape.")

        meta.end_time_ns = int(meta.start_time_ns + meta.deltat * self.nsamples * 1e9)
        self.meta = meta

    def write(
        self, file: Path | str, compress: bool = True, force: bool = False
    ) -> None:
        file = Path(file)
        if file.exists() and not force:
            raise OSError(f"{file} already exists, use force to overwrite")

        with h5py.File(file, "w") as container:
            logging.debug("Writing miniDAS to %s", file)
            dataset = container.create_dataset(
                "miniDAS",
                chunk=True,
                data=self.dataset,
                compress="lzf" if compress else False,
            )

            # dataset.dims[0].label = "channel"
            # dataset.dims[1].label = "time"

            dataset.attrs["version"] = self.version
            dataset.attrs.update(asdict(self.meta))

    @classmethod
    def is_valid(cls, file: Path | str) -> bool:
        file = Path(file)

        with h5py.File(file, "r") as container:
            dataset = container.get("miniDAS")
            if not dataset.attrs["version"] == cls.version:
                raise OSError(
                    f"file is version {dataset.attrs['version']},"
                    f" expected {cls.version}"
                )
        return True

    @classmethod
    def open(cls, file: Path | str):
        file = Path(file)
        if not cls.is_valid(file):
            raise AttributeError(f"{file} is not a miniDAS file.")

        container = h5py.File(file, "r")
        dataset = container.get("miniDAS")
        meta = dict(**dataset.attrs)
        meta.pop("version")

        instance = cls(dataset, Meta(**meta))
        instance._file = container
        return instance

    def close(self) -> None:
        if self._file:
            self._file.close()

    def get_data(self):
        return self.dataset[()]

    def get_dataset(self) -> h5py.Dataset:
        return self.dataset

    def get_time_slice(
        self,
        start_time: int,
        end_time: int,
        start_channel: int | None = None,
        end_channel: int | None = None,
    ) -> np.ndarray:
        meta = self.meta
        if start_time > end_time:
            raise AttributeError("end_time is before start_time")
        start_index = int((start_time - meta.start_time) // meta.deltat)
        end_index = int((end_time - meta.end_time) // meta.deltat)

        start_channel = start_channel or 0
        end_channel = end_channel or self.nchannels

        return self.dataset[start_channel:end_channel, start_index:end_index]

    @property
    def nchannels(self) -> int:
        return self.dataset.shape[0]

    @property
    def nsamples(self) -> int:
        return self.dataset.shape[1]

    @property
    def duration(self) -> float:
        return self.nsamples * self.meta.deltat
