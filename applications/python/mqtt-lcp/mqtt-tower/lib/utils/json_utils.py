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

                "..." : "include_file_name.json"

            Includes can be nested; i.e. an included file may itself contain includes.

The MIT License (MIT)

Copyright 2021 richard p hughes

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
INCLUDE_TOKEN = "\"...\""
COMMENT_TOKEN = "//"

import sys
import os

sys.path.append('../../lib')
import locale

import json


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
        json_lines = self.__load_file(file_name, "")
        # print(">>> JSON: " + str(json_lines))
        try:
            json_parsed = json.loads(json_lines)
        except json.decoder.JSONDecodeError as excp:
            print("!!!! JSON Parse Error: File: " + str(file_name))
            print(" ... " + str(excp))
            print(" ... " + str(json_lines))

        # print(">>> Json Parsed: "+str(json_parsed))
        return json_parsed

    #
    # private functions
    #

    def __load_file(self, file_name, indent):
        json_lines = ""
        #print(">>> Loading Json: "+ file_name)
        with open(file_name,
                  encoding=locale.getpreferredencoding(False)) as json_file:
            json_line_list = json_file.readlines()
            for json_line in json_line_list:
                new_line = json_line.rstrip()
                # print(">>> line: {"+str(sline)+"}")
                include_loc = new_line.find(INCLUDE_TOKEN)
                if include_loc != -1:
                    (include_file_name, new_indent) = \
                        self.__parse_include_file_name(new_line, indent)
                    # print(">>> include: " + str(include_file_name))
                    if os.path.sep in include_file_name:
                        # file name include a dir path, leave it alone
                        pass
                    else:
                        (fpath, _fname) = os.path.split(file_name)
                        if fpath != "":
                            include_file_name = fpath + os.path.sep + include_file_name
                    json_lines += new_indent + self.__load_file(
                        include_file_name, new_indent)
                    if new_line.endswith(","):
                        json_lines += new_indent + ","
                else:
                    if new_line.find(COMMENT_TOKEN) == -1:
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
