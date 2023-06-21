#!/usr/bin/python3
# json_utils.py
"""


    JsonUtils - funcs that aid in processing json files

    Load and parses standard JSON file but with two added nonstandard features:

        comments:

            A comment line is designated as:

              //  "this is a comment"

            Comments are single line only.

        includes:

            JSON files be included into other JSON files by specifiying:
                : include one json file:

                    "..." : "include_file_name.json"

                : or include all json file in a folder as a list:

                    " ..." : "include_folder_name"

            Includes can be nested; i.e. an included file may itself contain includes.

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
import json
import locale
import os
import sys
import pathlib

INCLUDE_TOKEN = "\"...\""
COMMENT_TOKEN = "//"


sys.path.append('../../lib')

from utils.global_constants import Global

class JsonUtils(object):
    """ help class for json operations """

    def __init__(self):
        pass

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def load_and_parse_file(self, file_name):
        """ loads and parses a json file, optionally including other files """
        json_parsed = None
        config_dir = False
        print("Parse: "+str(file_name))
        if file_name.endswith(".json"):
            # name is a single file, not a folder, parse it
            json_parsed = self.parse_one_json_file(file_name)
        else:
            # file name is a folder
            config_dir = os.listdir(file_name)
            #print(">>> config dir: "+str(config_dir))
            if "config.json" not in config_dir:
                print("!!! Error: Config.json not found in "+str(file_name))
            else:
                config_file_name = os.path.join(file_name, "config.json")
                # print(">>> Parsing: config file: "+ str(config_file_name))
                json_parsed = self.parse_one_json_file(config_file_name)
                #print(">>> json parsed: "+str(json_parsed))
                print("config dir: "+str(config_dir))
                for jfile in config_dir:
                    # load device configs
                    if jfile != "config.json" and \
                                jfile.endswith(".json") and \
                                jfile.startswith(Global.DEVICE) :
                        #print("parse sub file: "+str(jfile))
                        io_parsed = self.parse_one_json_file(
                                os.path.join(file_name, jfile))
                        if not isinstance(io_parsed,list):
                            io_parsed = [io_parsed]
                        for device_item in io_parsed:
                            json_parsed[Global.CONFIG][Global.IO]\
                                [Global.IO_DEVICES].append(device_item)
        #print(">>> json_parsed: "+str(json_parsed))
        return json_parsed

    def parse_one_json_file(self, file_name):
        """ read and parse a json file """
        json_parsed = None
        json_lines = self.__load_file(file_name, "")
        # print(">>> JSON: " + str(json_lines))
        try:
            json_parsed = json.loads(json_lines)
        except Exception as ex:
            print("!!!! JSON Parse Error: File: " + str(file_name))
            print(" ... " + str(ex))
            print(" ... " + str(json_lines))
        return json_parsed

    #
    # private functions
    #



    def __load_file(self, file_name, indent):
        """ load a file for all file in a folder """
        json_lines = ""
        # print("Loading JSON: " + file_name)
        if os.path.isdir(file_name):
            comma = ""
            for sub_file_name in os.listdir(file_name):
                extension = pathlib.Path(sub_file_name).suffix
                if extension.lower() in [".json"]:
                    incl_dir_file_name = file_name + os.path.sep + sub_file_name
                    json_lines += comma
                    comma = ","
                    json_lines += indent + self.__load_file(
                        incl_dir_file_name, indent)
        else:
            json_lines += self.__load_one_file(file_name, indent)
        return json_lines

    def __load_one_file(self, file_name, indent):
        """ load just one file """
        json_lines = ""
        # print("Loading JSON: " + file_name)
        with open(file_name,
                  encoding=locale.getpreferredencoding(False)) as json_file:
            json_line_list = json_file.readlines()
            for json_line in json_line_list:
                new_line = json_line.rstrip()
                # print(">>> line: {"+str(sline)+"}")
                trim_new_line = new_line.strip()
                # print(">>> time line: " + str(trim_new_line))
                if trim_new_line.startswith(INCLUDE_TOKEN):
                    (include_file_name, new_indent) = \
                        self.__parse_include_file_name(new_line, indent)
                    if os.path.sep in include_file_name:
                        # file name include a dir path, leave it alone
                        pass
                    else:
                        (fpath, _fname) = os.path.split(file_name)
                        if fpath != "":
                            include_file_name = fpath + os.path.sep + include_file_name
                    # print("Include JSON file: " + str(include_file_name))
                    json_lines += new_indent + self.__load_file(
                        include_file_name, new_indent)
                    if new_line.endswith(","):
                        json_lines += new_indent + ","
                else:
                    if not trim_new_line.startswith(COMMENT_TOKEN):
                        # ignore comments
                        #print(">>> Json Line: "+ str(json_line))
                        json_lines += indent + new_line
        #print(">>> json lines: "+str(json_lines))
        return json_lines

    def __parse_include_file_name(self, json_line, indent):
        """ parse out include file name from "...": "file_name" """
        include_indent = json_line.split(INCLUDE_TOKEN)[0]
        include_file_name = json_line.split(":")[1].strip()
        if include_file_name[:1] == "\"":
            # name is quoted, strip quotes
            endq = include_file_name.rfind("\"")
            include_file_name = include_file_name[1:endq]
            # print(">>> inc file: [" + str(include_file_name) + "]")
        new_indent = include_indent + indent
        return (include_file_name, new_indent)
