
Convert a csv table with geographical information to osm format.  
This script import few feature from csv2osm... In any case there is the possibility to serialize a csv compatible with csv2osm.

Dependencies:

  - Python 3
  - pyproj (`sudo apt-get install python3-pyproj` on Debian/Ubuntu)

Usage
-----

	usage: jcsv2osm.py
	
	output: output/NameOfCsv/
								+ NameOfCsv.csv 				# csv2osm compatible file
								+ NameOfCsv.json 				# json containing processed (success) records
								+ NameOfCsv_nodes_temp.json 	# json containing processed (incomplete) records
								+ NameOfCsv.osm					# osm file containing processed (success) records

	Following json are needed:
	
	"settings.json" : contain info about what to serialize and files to use
		
		{
			"csvFileName":"test.csv", 					# String - Name of csv file to process
			"csvDelimiter": ";", 						# String - Describe how value are separate: ",", ";" and so on
			"csvQuote": " ",							# String - Describe how value are quoted: "", "\"", "\'"
			"dictionaryFileName":"dictionary.json", 	# String - Name of Dictionary json
			"captionFileName":"caption.json",			# String - Name of Headers json
			"incompleteRecords": true,					# Boolean value - Tell if a json file containing processed (incomplete) records should be saved *
			"completeRecords": true,					# Boolean value - Tell if a json file containing processed (success) records should be saved
			"osmfile": true,							# Boolean value - Tell if a osm file containing processed (success) records
			"csv2osm": true								# Boolean value - Tell if a csv file compatible with csv2osm file should be saved
		}
	
	* Note: I'll explain what's the content of this file later.
		
	
	
	"dictionary.json"
	
		{
			"languageDict": "it_IT",   					# Value used for terms searching. In this case search algorithm will look for italian terms
			"dictionary": [								# List of items. Each item contain a term stuctured as follow:
				{
					"it_IT": "categoria",				# Italian value
					"fr_FR": "catégorie"				# French value
					"en_EN": "category",				# English value
					"osm_tag": [						# List of matching OSM_tags expressed as an object as follow:
						{
							"k": "key",					# k: key value for example "amenity"
							"v": "value"				# v: value associated to k for example "bar"
						},
						{
							"k": "key2",
							"v": "value"
						}
					]
				}
		}
		
	
	"caption.json"
	
	This file tell to the script which column need to procees in order to produce an osm/csv file. It's a List of object as follow:
	
	[
		{	
            "label": "name",						# This represent a well know key (or header for csv file output) for an osm TAG **
            "header": "nomeAttrattore",				# This represent the Header label that will be stored in "label"
            "useDictionary": false					# This tell to the script if dictionary is needed for find an appropriate tag...
        },
        {
            "label": "",
            "header": "risorsaTerritoriale",
            "useDictionary": true
        }
	]
	
	**Note: "label" is mandatory if useDictionary is false! 
			This because if we have a column h which value (for a row) is v, we need to say map each value(v) of h in the well know k ("label") in order to have a pair k = v in output file.
			
			
			Viceversa, if use dictionary is true, label is not mandatory. It will be skipped because the key is stored in the dictionary!
			For example:
			
			nomeAttrattore 	| Category
				"AAAA"		  "bar"
				"BBBB"		 "church"
			
			in the first column each value of "nomeAttrattore" will be mapped in  "label" nome.
			for the second column we can't express a unique "label" for every term, but we need to find the right pair of (k,v) associated to each value of category.
			Assuming that the term is stored in dictionary, "bar" will be converted in "amenity":"bar" (tag which match "bar" in osm) and so on...
			

	OUTPUT FILE: csvname_nodes_temp.json <incompleteRecords>
	
	This file contain records which for some reason have been not correctly processed, such as: no tags found in dictionary when a search occurred.
	It also contain value of unkonw value associated to "no result found".
	This is usefull for fill the dictionary with these unknow terms, and after that, the script can be runned again.
	At this point, we are asked to continue the processing (csvname_nodes_temp.json is parsed) - so only the nodes that previosly have been not processed will be taken - or re process the entire csv.
	BEWARE in both option every file will be rewrite. So if you choose to continue, it's better you save current files.
		
		