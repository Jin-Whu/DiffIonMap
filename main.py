# coding:utf-8
"""Main."""

import ReadConfig
import ReadIONEX
import IONEXPlot


# read configure file
read_config = ReadConfig.ReadConfig()
if not read_config.read():
    print 'Read configure file failed!'
    exit()

# retrieve all IONEX file
ionex_file = list()
for filepath, code in zip(read_config.filepath[:2], read_config.code):
    filelist = ReadIONEX.retrieveIONEX(filepath, code)
    if not filelist:
        print 'Retrieve IONEX file form %s failed!' % filepath
        exit()
    ionex_file.append(filelist)

# retrieve consistent doy ionex file
ionex_file_groups = ReadIONEX.retrievegroup(ionex_file)
if not ionex_file_groups:
    print 'Retrieve IONEC file group failed!'
    exit()

# start read ionexfile
for doy in ionex_file_groups:
    ionex_plotdata = list()
    for filepath in ionex_file_groups[doy]:
        read_ionex = ReadIONEX.ReadIONEX(filepath)
        if not read_ionex.read():
            print 'Read IONEX data from %s failed!' % read_ionex.filepath
        ionex_plotdata.append(read_ionex.ionexdata)
    ionex_plot = IONEXPlot.IONEXPlot(read_config.filepath[-1])
    ionex_plot.plot(ionex_plotdata)
print 'All done!'
