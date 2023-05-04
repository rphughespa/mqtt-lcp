
# json_utils.py
"""


    JsonUtils - funcs that aid in processing json files
        Assume the main config file is config/config.json
        Other io device configs are alos located the the config folder.
        Each io device config is parsed separately and merged into the main config dict


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
import os

from global_constants import Global


class JsonUtils(object):
    """ help class for json operations """

    def __init__(self):
        pass


    def load_and_parse_file(self, file_name):
        """ loads and parses a json file, optionally including other files """
        json_parsed = None
        config_dir = False
        print("Parse: "+str(file_name))
        if file_name.endswith(".json"):
            # name is a single file, not a folder, parse it
            json_parsed = self.__parse_one_json_file(file_name)
        else:
            # file name is a folder
            config_dir = os.listdir(file_name)
            print(">>> config dir: "+str(config_dir))
            if "config.json" not in config_dir:
                print("!!! Error: Config,json not found in "+str(file_name))
            else:
                config_file_name = file_name + "/" +"config.json"
                print(">>> Parsing: config file: "+ str(config_file_name))
                json_parsed = self.__parse_one_json_file(config_file_name)
                print(">>> json parsed: "+str(json_parsed))
                for jfile in config_dir:
                    # load device configs
                    if jfile != "config.json" and \
                       jfile.endswith(".json") and \
                       jfile.startswith("device") :
                        print("parse sub file: "+str(jfile))
                        io_parsed = self.__parse_one_json_file(file_name+"/"+jfile)
                        json_parsed[Global.CONFIG][Global.IO][Global.IO_DEVICES].append(io_parsed)
        return json_parsed

    def __parse_one_json_file(self, jname):
        """ open and parse a json file """
        print("Parsing JSON: "+str(jname))
        json_parsed = None
        jfile = open(jname)
        try:
            json_parsed = json.load(jfile)
        except ValueError as excp:
            print("!!!! JSON Parse Error: File: " + str(jname))
            print(" ... " + str(excp))
        jfile.close()
        return json_parsed
