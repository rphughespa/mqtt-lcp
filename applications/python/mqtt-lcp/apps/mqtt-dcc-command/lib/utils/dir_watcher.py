#!/usr/bin/python3
# dir_watcher.py
"""


   DirWatcher.py - watch a directory(folder) for changes

The MIT License (MIT)

Copyright 2023 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""

import sys
import os

sys.path.append('../../lib')

from utils.global_constants import Global


class DirWatcher(object):
    """ help class for logging operations """
    def __init__(self, dir_name):
        self.dir_name = dir_name
        self.last_directory = None

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def has_changed(self):
        """ have there been any changes in directory """
        changed = False
        new_list = {}
        if self.dir_name is not None:
            #print(">>> watch folder: "+str(self.dir_name))
            file_list = os.listdir(self.dir_name)
            #print(">>> watch files: "+str(file_list))
            for f in file_list:
                fkey = f + ":" + str(os.path.getmtime(os.path.join(self.dir_name, f)))
                new_list[fkey] = None
            if self.last_directory is not None:
                added = [f for f in new_list if not f in self.last_directory]
                removed = [f for f in self.last_directory if not f in new_list]
                if len(added) != 0 or len(removed) != 0:
                    changed = True
            self.last_directory = new_list
        return changed
