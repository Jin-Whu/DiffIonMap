# coding:utf-8
"""Read configure file."""

import os


class ReadConfig(object):
    """ReadConfi Class."""

    def __init__(self):
        """Initialize ReadConfig."""
        self.filepath = list()
        self.code = list()

    def read(self):
        """Read configure file."""
        configure_filepath = os.path.join(
            os.path.dirname(__file__), 'configure.ini')
        if not os.path.exists(configure_filepath):
            print 'Configure file is missing!'
            return 0

        try:
            with open(configure_filepath) as f:
                lines = f.readlines()
                self.filepath.append(lines[2].split('=')[1].strip())
                self.code.append(lines[3].split('=')[1].strip())
                self.filepath.append(lines[4].split('=')[1].strip())
                self.code.append(lines[5].split('=')[1].strip())
                self.filepath.append(lines[6].split('=')[1].strip())
            return 1
        except Exception as e:
            print e.message
            return 0
