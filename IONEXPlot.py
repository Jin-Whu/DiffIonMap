# coding:utf-8
"""Polt TEC Map."""

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import interp
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np
import os
import re


class IONEXPlot(object):
    """IONEXPlot Class."""

    def __init__(self, filepath):
        """Initialize IONEXPlot."""
        self.filepath = filepath

    def plot(self, ionex_plotdata):
        """Plot TEC Map for doy."""
        # find comman area of two ionedata
        latrange, lonrange = getarea(ionex_plotdata[0], ionex_plotdata[1])
        for time in ionex_plotdata[0]:
            if time not in ionex_plotdata[1]:
                continue

            # start plot
            fig = plt.figure(figsize=(20, 10))
            grid = ImageGrid(
                fig,
                111,
                nrows_ncols=(1, 2),
                share_all=True,
                axes_pad=0.3,
                cbar_location="right",
                cbar_mode="single",
                cbar_size="5%",
                cbar_pad=0.1, )
            for ax, i in zip(grid, [0, 1]):
                m = Basemap(
                    # projection='mill',
                    llcrnrlat=latrange[0],
                    urcrnrlat=latrange[-1],
                    llcrnrlon=lonrange[0],
                    urcrnrlon=lonrange[-1],
                    resolution='c',
                    ax=ax)
                m.drawcoastlines(color='#D3D3D3')
                m.drawcountries(color='#D3D3D3')
                parallels, meridians = getparmer(latrange, lonrange)
                if i == 0:
                    m.drawparallels(
                        parallels,
                        labels=[1, 0, 0, 0],
                        linewidth=0,
                        size=16,
                        weight='bold')
                m.drawmeridians(
                    meridians,
                    labels=[0, 0, 0, 1],
                    linewidth=0,
                    size=16,
                    weight='bold')

                tecmap = ionex_plotdata[i][time]
                # interpolate tecmap
                lon_inter, lat_inter, tecmap_inter = interpolate(tecmap)
                mpcolor = m.pcolormesh(
                    lon_inter,
                    lat_inter,
                    tecmap_inter,
                    latlon=True,
                    vmin=0,
                    vmax=100)

                # set title
                ax.set_title(ionex_plotdata[i].code, size=18, weight='bold')

            cbar = ax.cax.colorbar(mpcolor)
            cbar.ax.set_title('TECU', size=14, weight='bold')
            for l in cbar.ax.yaxis.get_ticklabels():
                l.set_weight("bold")
                l.set_fontsize(15)

            strdatetime = time.strftime('%Y-%m-%d %H:%M:%S')
            fig_title = '%s VS %s At %s' % (
                ionex_plotdata[0].code, ionex_plotdata[1].code, strdatetime)

            # suptitle postition
            suptitle_p = 0.75 if latrange[-1] - latrange[0] >= 160 else 0.8
            fig.suptitle(fig_title, size=22, weight='bold', y=suptitle_p)

            # save figure
            if not os.path.exists(self.filepath):
                os.makedirs(self.filepath)
            fig_name = '-'.join(re.split('[\s+:]', fig_title))
            fig_path = os.path.join(self.filepath, fig_name + '.png')
            fig.savefig(fig_path, bbox_inches='tight')
            plt.clf()
            plt.close()


def getarea(ionexdata1, ionexdata2):
    """Get area using given lat_range and lon_range.

    Args:
        lat_range: A list of lat range including lat1, lat2 and dlat.
        lon_range: A list of lon range including lon1, lon2 and dlon.

    Return:
        A tuple of latrange and lonrange.Latrange and lonrange is list.
    """
    latrange1 = sorted(ionexdata1.lat_range[:2])
    lonrange1 = sorted(ionexdata1.lon_range[:2])
    latrange2 = sorted(ionexdata2.lat_range[:2])
    lonrange2 = sorted(ionexdata2.lon_range[:2])
    lllat = max([latrange1[0], latrange2[0]])
    urlat = min(latrange1[1], latrange2[1])
    lllon = max(lonrange1[0], lonrange2[0])
    urlon = min(lonrange1[1], lonrange2[1])
    return [lllat, urlat], [lllon, urlon]


def getparmer(latrange, lonrange):
    """Get parallels and meridians."""
    parallels = np.round(np.linspace(latrange[0], latrange[1], 5))
    meridians = np.round(np.linspace(lonrange[0], lonrange[1], 7))
    # global range
    if parallels[-1] - parallels[0] > 160:
        parallels = np.round(parallels, -1).tolist()
        parallels = map(lambda x: x + 10 if x < 0 else x, parallels)
        parallels = map(lambda x: x - 10 if x > 0 else x, parallels)
    if meridians[-1] - meridians[0] > 350:
        meridians = np.round(meridians, -1)
        meridians = map(lambda x: x + 20 if x < 0 else x, meridians)
        meridians = map(lambda x: x - 20 if x > 0 else x, meridians)

    # normalize if interval greater than 10, less than
    if 10 <= (parallels[-1] - parallels[0]) / 4 <= 20:
        parallels = np.round(parallels, -1).tolist()
        interval = round((parallels[-1] - parallels[0]) / 4, -1)
        for i in range(1, len(parallels)):
            if parallels[i] - parallels[i - 1] > interval:
                parallels.insert(i, parallels[i - 1] + interval)
            elif parallels[i] - parallels[i - 1] < interval:
                parallels.remove(parallels[i])
                parallels.insert(i, parallels[i - 1] + interval)

    if 10 <= (meridians[-1] - meridians[0]) / 6 <= 20:
        meridians = np.round(meridians, -1).tolist()
        interval = round((meridians[-1] - meridians[0]) / 6, -1)
        for i in range(1, len(meridians)):
            if meridians[i] - meridians[i - 1] > interval:
                meridians.insert(i, meridians[i - 1] + interval)
            elif meridians[i] - meridians[i - 1] < interval:
                meridians.remove(meridians[i])
                meridians.insert(i, meridians[i - 1] + interval)
        # move 5°
        meridians = [x + 5 for x in meridians if x + 5 < lonrange[1]]
    return parallels, meridians


def interpolate(tecmap):
    """Interpolate TEC Map."""
    lat2 = np.linspace(tecmap.lat[0][0], tecmap.lat[-1][0],
                       tecmap.lat.shape[0] * 10)
    lon2 = np.linspace(tecmap.lon[0][0], tecmap.lon[0][-1],
                       tecmap.lon.shape[1] * 20)
    lon_inter, lat_inter = np.meshgrid(lon2, lat2)
    tecmap_inter = interp(
        tecmap.value,
        tecmap.lon[0],
        np.flipud(tecmap.lat[:, 0]),
        lon_inter,
        np.flipud(lat_inter),
        order=1)
    return lon_inter, lat_inter, tecmap_inter
