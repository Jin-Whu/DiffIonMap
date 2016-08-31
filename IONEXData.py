# coding:utf-8
"""IONEXData structure."""

import numpy as np
from collections import OrderedDict


class IONEXData(OrderedDict):
    """IONEXData."""

    def __init__(self, lat_range, lon_range, code):
        """Initialize IONEXData."""
        self.lat_range = lat_range
        self.lon_range = lon_range
        self.code = code
        super(IONEXData, self).__init__()

    def tecmaprow(self):
        """Return TEC Map row."""
        return len(
            np.arange(self.lat_range[0], self.lat_range[1] + self.lat_range[2],
                      self.lat_range[2]))

    def tecmapcol(self):
        """Retrun TEC Map col."""
        return len(
            np.arange(self.lon_range[0], self.lon_range[1] + self.lon_range[2],
                      self.lon_range[2]))


class TECMapData(object):
    """IonMapData."""

    def __init__(self, map_id, time, exponent):
        """Initialize IonMapData."""
        self.map_id = map_id
        self.time = time
        self.exponent = exponent
        self.lat = list()
        self.lon = list()
        self.h = list()
        self.value = list()

    def add(self, lat, lon, h, value):
        """Add value to IonMapData."""
        self.lat.append(lat)
        self.lon.append(lon)
        self.h.append(h)
        self.value.append(value * 10**self.exponent)

    def reshape(self, row, col):
        """Reshape to grid data."""
        self.lat = np.array(self.lat).reshape(row, col)
        self.lon = np.array(self.lon).reshape(row, col)
        self.value = np.array(self.value).reshape(row, col)
