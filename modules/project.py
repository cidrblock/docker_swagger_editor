import os
from modules.print_in_color import PrintInColor
import shutil

class Project(object):
    def __init__(self, directory):
        self.directory = directory

    def make_directory(self, directory, clobber=False):
        new_directory = "%s/%s" % (self.directory, directory)
        try:
            os.stat(new_directory)
            PrintInColor.message(color='GREEN', action="exists", string=new_directory)
        except OSError:
            clobber = True
        if clobber:
            os.mkdir(new_directory)
            PrintInColor.message(color='YELLOW', action="created", string=new_directory)

    def remove_trailing_whitespace(self, directory=None):
        if not directory:
            directory = self.directory
        for path, dirs, file_names in os.walk(directory):
            for file_name in file_names:
                _file_name, file_extension = os.path.splitext(file_name)
                if file_extension == '.py':
                    path_name = os.path.join(path, file_name)
                    with open(path_name, 'r') as fh:
                        new = [line.rstrip() for line in fh]
                    with open(path_name, 'w') as fh:
                        [fh.write('%s\n' % line) for line in new]
            for subdir in dirs:
                self.remove_trailing_whitespace(directory="%s%s" % (path, subdir))
