import json
import logging
import difflib


class Dictionary:


    __data = None   #Dictionary data
    __d = None      #Dictionary Name
    __tags = None
    __dCat = None
    __index = 0


    def __init__(self, dictName):
        self.__d = dictName
        try:
            with open(dictName) as json_data:
                logging.info("Dictionary file '" + self.__d + "' FOUND.")
                self.__data = json.load(json_data)
                #logging.info("Il dizionario 'dictionary.json' trovato. Importo i termini.")
                del json_data
        except EnvironmentError:
            logging.info("Dictionary file '" + self.__d + "' NOT FOUND.")

    def searchTerm(self, word):
        logging.info("[DICTIONARY] Checking if  " + word.upper() + " is in Dictionary >> " + self.__d)
        self.__tags = None
        cat = ""
        maxRatio = 0

        for term in self.__data["dictionary"]:
            ratio = difflib.SequenceMatcher(None, term[self.__data["languageDict"]], word).ratio()
            #0.6 è una soglia di default per dire che due stringhe sono simili.
            if ratio > 0.6 and ratio > maxRatio:
                self.__tags = term["osm_tag"]
                cat = term[self.__data["languageDict"]]
                maxRatio = ratio
                #return self.__dCat

        if self.__tags == None:
            logging.info("[DICTIONARY] No Matching found for ... " + word + ".")
            return 0
        else:
            logging.info("[DICTIONARY] Matching found! >>  " + word.upper() + "  matches @ " + str(maxRatio*100) + "% the word in dictionary " + cat.upper() + ".")
            return 1

    def getFoundTag(self):
        return self.__tags

    #DA CONTROLLARE
    def addTerm(self, wordIT, wordEN, tags):
        logging.info("Aggiungo la categoria '" + wordIT + "' al dizionario.")
        if self.searchTerm(wordIT):
            self.addTag(self.__index, tags)
            logging.info("Tag aggiunti alla categoria " + self.__dCat + " esistente.")
        else:
            self.addNewTerm(wordIT, wordEN, tags)


    def addNewTerm(self, wordIT, wordEN, tags):
        item = {
            "it_term": wordIT,
            "en_term": wordEN,
            "osm_tag": tags
        }
        self.__data.append(item)
        logging.info("Nuova categoria '" + wordIT + "' aggiunta al dizionario.")

    def addTag(self, i, tags):
        self.__data[i]["osm_tag"].append(tags)

    def saveDictionary(self):
        with open(self.__d, 'w') as outfile:
            json.dump(self.__data, outfile, indent=4)