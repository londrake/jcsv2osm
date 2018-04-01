import csv
import json
import logging
from support import dictionary
"""Import from csv 2 osm"""
from pyproj import Proj, transform
import re, locale
from xml.sax.saxutils import quoteattr

class Csv2JsOsm:

    __csvFileName = ""
    __captionFileName = "caption.json"
    __dictFileName = "dictionary.json"
    __readCSV = "" # csv Readed
    __data = None # caption JSON
    __d = None # dictionary istance
    __missingColumn = [] #Array of missing column
    __delimiter = None #csv delimiter
    __quotechar = None #csv quotechar
    __catNotFound = [] #Array of missing category in dictionary
    __dataNotFound = [] #Array of record which no categories have been found
    __dataExtracted = [] #array of record correctly processed
    __item = {} #item processed
    __output = "" #output path
    __keys = {} #all keys faced




    def open(self, csvFileName, delimiter, quotechar):
        self.__csvFileName = csvFileName
        try:
            with open(csvFileName, newline='') as csvfile:
                self.__readCSV = list(csv.DictReader(csvfile, delimiter=delimiter, quotechar=quotechar))
                logging.info("File csv '" + csvFileName + "' aperto correttamente.")
            return 1
        except FileNotFoundError and csv.Error as e:
            logging.info("ERROR: Error occurred while opening dataset.")
            logging.info(e)
            return 0

    def process(self):
        if not self.__findMainKey(self.__readCSV[0]):
            return 0
        logging.info("")
        logging.info("HEADER'S FIELD Check: DONE with success! \n")

        if self.__missingColumn:
            logging.error("ERROR: Cannot find these colums: " + ", ".join(self.__missingColumn) + ". Check your CSV/Caption file.")
            logging.info("HINT: add/check labels in CAPTION FILE!")
            return 0
        else:
            self.__dataExtracted = []
            self.__dataNotFound = []
            logging.info(str(len(self.__readCSV)) + " RECORD TO PROCESS.\n")
            i = 1
            for row in self.__readCSV:
                logging.info(">>>>>>>>>> RECORD " + str(i) + " <<<<<<<<<< \n")
                try:
                    if self.__dataProcess(row):
                        self.__dataExtracted.append(self.__getItem())
                    else:
                        self.__dataNotFound.append(self.__getItem())
                    i += 1
                    logging.info(">>>>>>>>>> DONE  <<<<<<<<<< \n")
                except KeyError:
                    logging.info(">>>>>>>>>> ERROR  <<<<<<<<<< \n")
                    return 0
            return 1

    def __dataProcess(self, row):
        item = {}
        item2 = {}
        catfound = False
        for element in self.__data:
            h = element["header"]
            v = str(row[h].replace('\"', '\\"'))
            item2[h] = v
            if not v == "":
                if element["useDictionary"]:
                    if self.__d.searchTerm(v):
                        catfound = True
                        tags = self.__d.getFoundTag()
                        for tag in tags:
                            k = tag["k"]
                            v = tag["v"]
                            item[tag["k"]] = tag["v"]
                            self.__addHeader(tag["k"])
                    else:
                        k = str(element["label"])
                        self.__catNotFound.append(v)
                        item[h] = v
                else:
                    k = str(element["label"])
                    item[k] = v
                    self.__addHeader(k)
                logging.info(h + " => " + k + " = " + v + ".")
        if not catfound:
            self.__item = item2
        else:
            self.__item = item
        return catfound

    def __addHeader(self, h):
            self.__keys[h] = ""

    def __getItem(self):
        return self.__item

    def getData2Process(self):
        return self.__dataExtracted

    def setData2Process(self, records):
        self.__readCSV = records

    def __findMainKey(self, captionRow):
        logging.info("Checking HEADER'S FIELD... \n")
        for caption in self.__data:
            try:
                if captionRow[caption["header"]] and (not caption["useDictionary"]) and caption["label"] == "":
                    logging.error("Label for " + caption["header"] + " is mandatory.")
                    return 0
                else:
                    label = " on that field dictionary will be used."
                    if not caption["label"] == "":
                        label = caption["label"] + "."
                    logging.info("HEADER FOUND: " + caption["header"] + " => " + label)
            except KeyError:
                logging.error("HEADER NOT FOUND : " + caption["header"])
                self.__missingColumn.append(caption["header"])
                continue
        return 1


    def loadConfiguration(self):
        try:
            with open(self.__captionFileName) as json_data:
                self.__data = json.load(json_data)
                logging.info("Configuration file '" + self.__captionFileName + "' FOUND.")
                del json_data
        except EnvironmentError:
            logging.error("Configuration file '" + self.__captionFileName + "' NOT FOUND.")

        self.__d = dictionary.Dictionary(self.__dictFileName)

    def updateSettings(self, data, output):
        if not data["csvFileName"] == "":
            self.__csvFileName = data["csvFileName"]
        if not data["captionFileName"] == "":
            self.__captionFileName = data["captionFileName"]
        if not data["dictionaryFileName"] == "":
            self.__dictFileName = data["dictionaryFileName"]
        if not output == "":
            self.__output = output

    def csv2JsonComplete(self):
        logging.info("Writing Json file for complete record")
        self.__csv2json("", self.__dataExtracted)

    def csv2JsonIncomplete(self):
        if len(self.__catNotFound) > 0 or len(self.__dataNotFound):
            logging.info("Writing Json file for incomplete record")
            jjson = {"categoriesNotFound": self.__catNotFound, "records": self.__dataNotFound}
            self.__csv2json("_nodes_temp", jjson)

    def __csv2json(self, filename, nodes):
        if len(nodes) > 0:
            try:
                with open(self.__output + self.__csvFileName + filename + ".json", 'w') as outfile:
                    json.dump(nodes, outfile, indent=4)
            except EnvironmentError:
                logging.error("ERROR: Something went wrong!!!")
            logging.info("Done.")
        else:
            logging.info("JSON: Nothing to write...")

    def writeCSV(self):
        logging.info("Writing csv2osm file with complete record")
        if len(self.__dataExtracted) > 0:
            #keys = self.__keys.keys()
            with open(self.__output + self.__csvFileName, 'w') as f:  # Just use 'w' mode in 3.x
                w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                w.writerow(self.__keys)
                for n in self.__dataExtracted:
                    temp = []
                    for k in self.__keys:
                        try:
                            temp.append(n[k])
                        except KeyError:
                            temp.append("")
                    w.writerow(temp)
                logging.info("Done.")
        else:
            logging.info("CSV: Nothing to write...")

    def json2osm(self):
        logging.info("Writing osm file with complete record")
        if len(self.__dataExtracted) > 0:
            proj_out = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs +towgs84=0,0,0')
            proj_in = proj_out
            try:
                xkey = [i for i in ["LONGITUDE", "longitude", "lon", "x", "e", "Longitudine"] if i in self.__keys]
                ykey = [i for i in ["LATITUDE", "latitude", "lat", "y", "n", "Latitudine"] if i in self.__keys]
            except:
                logging.info('Error: Coordinate fields not found in the csv file header.')
            with open(self.__output + self.__csvFileName + ".osm", 'w') as f:
                #f.write()
                print('<?xml version="1.0" encoding="UTF-8"?><osm version="0.6" generator="jcsv2osm">', file=f)
                i = 0
                for n in self.__dataExtracted:
                    i = i-1
                    try:
                        (lon, lat) = transform(proj_in, proj_out, self.parse_coord(n[xkey[0]]), self.parse_coord(n[ykey[0]]))
                    except:
                        logging.error("Skipping node {}: couldn't parse coordinates".format(i))
                        continue
                    print('<node id="{}" lat="{}" lon="{}">'.format(i, lat, lon), file=f)
                    for key in n:
                        if n[key] and (key not in [xkey[0], ykey[0]]):
                            """Luca Start Edit"""
                            if "-|-" in n[key]:
                                tags = n[key].split("-|-")
                                for tag in tags:
                                    print('<tag k="{}" v={}/>'.format(key, quoteattr(tag)), file=f)
                            else:
                                """ End Edit"""
                                print('<tag k="{}" v={}/>'.format(key, quoteattr(n[key])), file=f)
                    print('</node>', file=f)
                print('</osm>', file=f)
                logging.info("Done.")
        else:
            logging.info("csv2osm: Nothing to write...")

    def parse_coord(self, c):
        parse_dms = re.compile(r'''(?P<pre>[NSWE+-]?)\s?(?P<deg>\d+)(?:°|º|\s?deg)\s?(?P<min>\d+)(?:'|’| )\s?(?P<sec>[\d,.]+)(?:"|”)?\s?(?P<post>[NSWE]?)''')
        try:
            return locale.atof(c)
        except:
            m = parse_dms.match(c)
            if m.group('post') and m.group('pre'):
                h = None
            elif m.group('post') in ['S', 'W'] or m.group('pre') in ['-', 'S', 'W']:
                h = -1
            elif m.group('post') in ['N', 'E'] or m.group('pre') in ['+', 'N', 'E'] \
                    or not (m.group('post') and m.group('pre')):
                h = 1
            return h * (locale.atof(m.group('deg')) + locale.atof(m.group('min'))/60 + locale.atof(m.group('sec'))/3600)


