#!/usr/bin/python3
# yaml_utils.py
"""


    YamlUtils - funcs that aid in processing yaml files

    Loads and parses standard YAML files but with two added nonstandard features:

        comments:

            A comment line is designated as:

            #  this is a comment

            Comments are single line only.
            The "#" must appear in col 1 of the test line

        includes:

            YAML files be included into other YAML files by specifiying:

                "...": "include include_file_name.yaml"

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

import os
import sys

import pathlib

import locale
import yaml



INCLUDE_TOKEN = "..."


sys.path.append('../../lib')


class YamlUtils(object):
    """ help class for yaml operations """

    def __init__(self):
        pass

    def __repr__(self):
        # return "%s(%r)" % (self.__class__, self.__dict__)
        fdict = repr(self.__dict__)
        return f"{self.__class__}({fdict})"

    def load_and_parse_file(self, file_name):
        """ loads and parses a yaml file, optionally including other files """
        yaml_parsed = None
        yaml_lines = self.__load_file(file_name, "")
        print(">>> yaml lines: \n" + str(yaml_lines))
        yaml_parsed = yaml.safe_load(yaml_lines)
        # print(">>> yaml Parsed: "+str(yaml_parsed))
        return yaml_parsed

    #
    # private functions
    #
    def __load_file(self, file_name, indent):
        """ load a file for all file in a folder """
        yaml_lines = ""
        # print("Loading YAML: " + str(file_name))
        if os.path.isdir(file_name):
            for sub_file_name in os.listdir(file_name):
                extension = pathlib.Path(sub_file_name).suffix
                print(">>> extension: " + str(extension))
                if extension.lower() in [".yaml", ".yml", ""]:
                    incl_dir_file_name = file_name + os.path.sep + sub_file_name
                    yaml_lines += indent + self.__load_file(
                        incl_dir_file_name, indent)
        else:
            yaml_lines += self.__load_one_file(file_name, indent)
        return yaml_lines

    def __load_one_file(self, file_name, indent):
        yaml_lines = ""
        print("Loading YAML: " + file_name)
        with open(file_name,
                  encoding=locale.getpreferredencoding(False)) as yaml_file:
            yaml_line_list = yaml_file.readlines()
            for yaml_line in yaml_line_list:
                # print(">>> line: {"+str(sline)+"}")
                include_loc = yaml_line.find(INCLUDE_TOKEN)
                if include_loc != -1:
                    (include_file_name, new_indent) = self.__parse_include_file_name(
                        yaml_line, indent)

                    if os.path.sep in include_file_name:
                        # file name include a dir path, leave it alone
                        pass
                    else:
                        print(">>> filename: "+str(file_name))
                        (fpath, _fname) = os.path.split(file_name)
                        if fpath != "":
                            include_file_name = fpath + os.path.sep + include_file_name
                    yaml_lines += new_indent + self.__load_file(
                        include_file_name, new_indent)
                else:
                    if not yaml_line.strip().startswith("#"):
                        # ignore comments
                        # print(">>> yaml Line: "+ str(yaml_line))
                        yaml_lines += indent + yaml_line
        # print(">>> yaml lines: "+str(yaml_lines))
        return yaml_lines

    def __parse_include_file_name(self, yaml_line, indent):
        """ parse out include file name from "...": "file_name" """
        print(">>> indent 1: " + str(len(indent)))
        include_splits = yaml_line.split(INCLUDE_TOKEN)
        include_indent = include_splits[0]
        print((">>> indent 2: " + str(len(include_indent))))
        include_file_name = include_splits[1].replace(
            ":", "").replace("\"", "").strip()
        # if include_file_name[:1] == "\"":
        #    # name is quoted, strip quotes
        #    include_file_name = include_file_name[1:-1]
        new_indent = include_indent + indent
        print(">>> indent 3: " + str(len(new_indent)))
        return (include_file_name, new_indent)
