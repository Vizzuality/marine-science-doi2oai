#!/usr/bin/env python3
import xmltodict
import os
import json
from datetime import datetime

JSON_DIR = "data"
metadata_format = "oai_dc"
current_datetime = datetime.now().isoformat()

def read_jsons(directory = JSON_DIR):
    """read all json files in the /data directory and return a list of json objects"""
    jsons = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath) as file:
                jsons[filename[:-5]] = json.load(file)
    return jsons

def prepare_oai_dict():
    """prepare the oai response dictionary"""
    oai_dict = {
        'OAI-PMH': {
            '@xmlns': 'http://www.openarchives.org/OAI/2.0/',
            '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            '@xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd',
            'responseDate': current_datetime,
            'request': {
                '@verb': 'ListRecords',
                '@metadataPrefix': metadata_format,
                '#text': 'https://dataverse.harvard.edu/oai'},
            'ListRecords': {
                'record': []
            }
        }
    }

    return oai_dict

def prepare_dc_json(doi, json):
    """Extract Dublin Core metadata from the json object and add it to the oai response"""

    #TODO map non-dc metadata to dublin core, verify which fields exist in Dataverse
    
    dc_json = {}
    identifier = None

    for key, value in json.items():
        key = key.lower().replace(".",":")
        if key.startswith("dc:"):
            dc_json[key] = value

        #FIND IDENTIFIER AS URL OR DOI
        if key.startswith("dc:identifier"):
            if type(value) is str:
                value = [value]
            for v in value:
                if key.startswith("dc:identifier:doi"):
                    if key.startswith("doi:"):
                        identifier = "http://doi.org/" + v.split("doi:")[1]
                    else:
                        identifier = "http://doi.org/" + v
                elif key.startswith("dc:identifier:uri"):
                    if key.startswith("http"):
                        identifier = key
                elif key == "dc:identifier":
                    if key.startswith("doi"):
                        identifier = "http://doi.org/" + v.split("doi:")[1]
                    elif key.startswith("http"):
                        identifier = key

    if identifier is None:
        print (f"DOI {doi} has no valid identifier")
        return {}
    if len(dc_json) == 0:
        print(f"DOI {doi} has no dc-prefixed metadata")
        return {}
    
    oai_dict = {
        'header': {
            'identifier': identifier,
            'datestamp': current_datetime,
        },
        'metadata': {
            'oai_dc:dc': {
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                '@xmlns:oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                '@xmlns:dc': 'http://purl.org/dc/elements/1.1/',
                '@xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
            }
        }
    }
    oai_dict['metadata']['oai_dc:dc'].update(dc_json)
    return oai_dict


def main():
    """reads json citation data and writes it to an XML file in OAI-PMH format"""
    oai_dict = prepare_oai_dict()
    jsons = read_jsons()
    for name, data in jsons.items():
        # TODO replace name from filename to doi
        oai_record = prepare_dc_json(name, data)
        oai_dict['OAI-PMH']['ListRecords']['record'].append(oai_record)

    with open("outputs/oai", "w") as file:
        file.write(xmltodict.unparse(oai_dict, pretty=True))

if __name__ == "__main__":
    main()