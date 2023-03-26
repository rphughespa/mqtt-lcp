#!/usr/bin/python3
# dashboard_info_list.py

"""

DashboardInfoList - Selectable info list of Dashboard items
the MIT License (MIT)

Copyright © 2020 richard p hughes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys

# import tkinter as tk
# import tkinter.ttk as ttk

#from utils.global_constants import Global

sys.path.append('../../lib')

# from image_button import ImageButton
# from components.local_constants import Local

from components.scrollable_info_list import ScrollableInfoList
from components.dashboard_info_box import DashboardInfoBox

class DashboardInfoList(ScrollableInfoList):
    """ scrollable info list """

    def __init__(self, parent, info_dict, **kwargs):
        """ initialize """
        # info_dict must have a "id" value and and a "description" value for each item

        super().__init__(parent, info_dict, **kwargs)

    def format_info_box(self, key, value):
        """ format a single list line """
        # values assumed to the a GuiMessage
        info_box = DashboardInfoBox(self.frame, key,
                                    height=self.row_height,
                                    title=value.node_id,
                                    description=value.description,
                                    image=value.image,
                                    name=value.node_id,
                                    callback=self.callback, width=self.width-4)
        return info_box
