"""Read IONEX File."""

# coding:utf-8

import os
import re
import datetime
import numpy as np
from collections import OrderedDict
import IONEXData


class ReadIONEX(object):
    """ReadIONEX Class."""

    def __init__(self, filepath):
        """Initialize."""
        self.filepath = filepath.filepath
        self.code = filepath.code
        self.ionexdata = None

    def read(self):
        """Read IONEX file."""
        # check filepath
        if not os.path.exists(self.filepath):
            print 'IONEX file %s not found' % self.filepath
            return 0

        try:
            # start read ionex file
            with open(self.filepath) as f:
                exponent = -1  # unit of ionsphere values

                # read ionex header
                for line in f:
                    # read epoch of first map and last map
                    # read interval
                    # read HGT1 / HGT2 / DHGT
                    # read LAT1 / LAT2 / DLAT
                    # read LON1 / LON2 / DLON
                    # read exponent
                    # if 'EPOCH OF FIRST MAP' in line:
                    #     epoch_first = convert2datetime(
                    #         re.split(r'EPOCH', line)[0].strip())
                    #
                    # if 'EPOCH OF LAST MAP' in line:
                    #     epoch_last = convert2datetime(
                    #         re.split(r'EPOCH', line)[0].strip())
                    #
                    # if 'INTERVAL' in line:
                    #     interval = int(line.split()[0])
                    #
                    # if 'HGT1 / HGT2 / DHGT' in line:
                    #     hgtgroup = re.split(r'HGT1', line)[0].strip().split()
                    #
                    if 'LAT1 / LAT2 / DLAT' in line:
                        lat_range = map(
                            float, re.split(r'LAT1', line)[0].strip().split())

                    if 'LON1 / LON2 / DLON' in line:
                        lon_range = map(
                            float, re.split(r'LON1', line)[0].strip().split())

                    if 'EXPONENT' in line:
                        exponent = float(line.split()[0])

                    if 'END OF HEADER' in line:
                        break

                # read ionex body (just read TEC MAP)
                ionex_data = IONEXData.IONEXData(lat_range, lon_range,
                                                 self.code)
                read_tec_map = 1
                for line in f:
                    if read_tec_map:
                        if 'START OF RMS MAP' in line:
                            break  # end of tecmap(codg, iscg)

                        if 'START OF TEC MAP' in line:
                            map_id = int(re.split(r'START', line)[0].strip())
                        if 'EPOCH OF CURRENT MAP' in line:
                            time = convert2datetime(
                                re.split(r'EPOCH', line)[0].strip())
                            tec_map = IONEXData.TECMapData(map_id, time,
                                                           exponent)
                            ionex_data[time] = tec_map
                        if 'LAT/LON1/LON2/DLON/H' in line:
                            lat_lon_h = line.replace('-', ' -').split()
                            lat = float(lat_lon_h[0])
                            lon1 = float(lat_lon_h[1])
                            lon2 = float(lat_lon_h[2])
                            dlon = float(lat_lon_h[3])
                            h = float(lat_lon_h[4])
                            read_tec_map = 0
                            ilon = 0
                            nlon = len(np.arange(lon1, lon2 + dlon, dlon))
                            read_tec_map = 0
                    else:
                        for value in [float(x) if x != '9999' else np.nan
                                      for x in line.split()]:
                            lon = lon1 + dlon * ilon
                            tec_map.add(lat, lon, h, value)
                            ilon += 1

                        if ilon == nlon:
                            read_tec_map = 1

            # reshap lat, lon to grid
            for tecmap in ionex_data.values():
                tecmap.reshape(ionex_data.tecmaprow(), ionex_data.tecmapcol())
            self.ionexdata = ionex_data
            return 1
        except Exception as e:
            print e.message
            return 0


class IONEXFilePath(object):
    """IONEXFilePath.

    Combine code and filepath.
    """

    def __init__(self, filepath, code):
        """Initialize IONEXFilePath."""
        self.filepath = filepath
        self.code = code


def retrieveIONEX(filepath, code):
    """Retrieve IONEX file from given filepath."""
    if not os.path.exists(filepath):
        print '%s not found' % filepath
        return 0

    try:
        reobj = re.compile(code + '(\d\d\d).\.\d+I', re.IGNORECASE)
        filelist = OrderedDict()
        for basepath, dirs, files in os.walk(filepath):
            for f in files:
                doy = reobj.findall(f)
                if doy:
                    filelist[doy[0]] = IONEXFilePath(
                        os.path.join(filepath, f), code)
        return filelist
    except Exception as e:
        print e.message
        return 0


def retrievegroup(filelist):
    """Retrieve consistent doy of two ionexfile sets.

    Arg:
        filelist: A list contain two dicts of ionex file of different code.

    Return:
        A dcit mapping doy to the corresponding ionexfiles.
    """
    retrieve_files = OrderedDict()
    for doy in filelist[0]:
        if doy in filelist[1]:
            retrieve_files[doy] = (filelist[0][doy], filelist[1][doy])
    return retrieve_files


def convert2datetime(s):
    """Convert datetime string to datetime."""
    year, month, day, hour, mintue, second = map(int, s.split())
    return datetime.datetime(year, month, day, hour, mintue, second)
