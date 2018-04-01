"""pip install overpy"""
from difflib import SequenceMatcher
import json
import os
import logging
import datetime
import time
from csv2table import csv2table

#csvFile = csv2table.Csv2JsOsm()


def main():

    # inizializzo il logger che scrive su file
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename= 'log' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H.%M.%S')+'.txt',
                        filemode='w')
    # definisco un  Handler che reindirizza gli INFO messages o livello superiore al sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # imposto la formattazione da usare e l'assegno al logger
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    # associo il nuovo logger a quello principale
    logging.getLogger('').addHandler(console)
    logging.info("INFO: A DETAILED FILE IS AVAIBLE IN ROOT FOLDER.")
    logging.info("OPENING SETTINGS FILE 'settings.json'")
    #Apro il file json con le configurazioni
    try:
        with open('settings.json') as json_data:
            data = json.load(json_data)
            del json_data
            logging.info("SETTINGS FILE 'settings.json' FOUND!. IMPORTING PARAMETERS...")
    except FileNotFoundError:
        logging.error("ERROR: SETTINGS FILE 'setting.json' NOT FOUND OR BAD FORMATTED.")
    #CHECK IF OUTPUT DIR EXIST
    directory("output")
    #CREATE A SUB DIR NAMED AS THE FILE
    path = "output/" + data["csvFileName"].replace(".", "_") + "/"
    if setting(data):
        #CHECK IF THERE IS A OLD SESSION WITH INCOMPLETE DATA
        directory(path)
        if not (checkFile(path + data["csvFileName"] + "_nodes_temp.json")):
            logging.info("TEMP FILE NOT FOUND")
            readCsv(path, data)
        else:
            logging.info("An old session have been found.  Continue? [y/n] >>>")
            if continuaExe():
                readJson(path, data)
            else:
                logging.info("Ignoring old session and opening csv file.")
                readCsv(path, data)

def readJson(path, data):
    csvFile = csv2table.Csv2JsOsm()
    try:
        with open(path + data["csvFileName"] + "_nodes_temp.json") as json_data:
            csvFile.setData2Process(json.load(json_data).get('records'))
            del json_data
            #del jjson
    except IOError:
        logging.info("ERROR: Json temp file NOT found.")
    csvFile.updateSettings(data, path)
    csvFile.loadConfiguration()
    logging.info("Reading JSON TEMP FILE file...")
    processData(csvFile, data, "_nodes_temp.json")

def readCsv(path, data):
    csvFile = csv2table.Csv2JsOsm()
    if csvFile.open(data["csvFileName"], data["csvDelimiter"], data["csvQuote"]):
        csvFile.updateSettings(data, path)
        csvFile.loadConfiguration()
        logging.info("Reading CSV file...")
        processData(csvFile, data, "")
        del csvFile
    else:
        logging.info("ERROR: Something went wrong while opening file " + data["csvFileName"])

def processData(csvFile, data, file):
    if csvFile.process():
        if data["completeRecords"]:
            csvFile.csv2JsonComplete()
        if data["csv2osm"]:
            csvFile.writeCSV()
        if data["osmfile"]:
            csvFile.json2osm()
        if data["incompleteRecords"]:
            csvFile.csv2JsonIncomplete()
        else:
            logging.info("ERROR: Something happened while processing data in " + data["csvFileName"] + file)


def setting(data):
    if not data["csvFileName"]:
        logging.info("No CSV file have been specified. Insert it in setting.json")
        return 0

    if not data["captionFileName"]:
        logging.info("No HEADERS file have been specified. Default file will be used.")
        data["csvFileName"] = "caption.json"

    if not data["dictionaryFileName"]:
        logging.info("No DICTIONARY file have been specified. Default file will be used.")
        data["dictionaryFileName"] = "dictionary.json"

    checkFile(data["captionFileName"])
    checkFile(data["dictionaryFileName"])
    return 1

def checkFile(filename):
    if os.path.exists(filename):
        return 1
    else:
        logging.error("File '" + filename + "' NOT FOUND.")
        return 0

def directory(directory):

    if os.path.isdir(os.getcwd() + "/" + directory):
        logging.info("Directory '" + directory + "' FOUND.")
        return 1
    else:
        logging.info("Directory '" + directory + "' NOT FOUND.")
        os.makedirs(os.getcwd() + "/" + directory)
        logging.info("Directory '" + directory + "' CREATED.")
        return 0

def continuaExe():
    continua = input("Continue? [y/n] >>> ")
    if continua.lower() in ["yes", "y", "1"]:
        return 1
    elif continua.lower() in ["no", "n", "0"]:
        return 0
    else:
        continuaExe()