#!/usr/bin/env python3
import xmltodict
import os
import json
from datetime import datetime

JSON_DIR = "data"
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
                '@metadataPrefix': 'oai_dc',
                '#text': 'https://dataverse.harvard.edu/oai'},
            'ListRecords': {
                'record': []
            }
        }
    }

    return oai_dict

def prepare_dc_json(doi, json):
    """prepare the citation json object"""
    
    dc_json = {}
    for key, value in json.items():
        key = key.lower().replace(".",":")
        if key.startswith("dc:"):
            dc_json[key] = value
            
    if len(dc_json) == 0:
        print(f"DOI {doi} has no dc-prefixed metadata")
        return {}
    
    oai_dict = {
        'header': {
            'identifier': doi,
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
    oai_dict = prepare_oai_dict()
    jsons = read_jsons()
    for k, data in jsons.items():
        oai_dict['OAI-PMH']['ListRecords']['record'].append(prepare_dc_json(k, data))

    with open("outputs/oai", "w") as file:
        file.write(xmltodict.unparse(oai_dict, pretty=True))

if __name__ == "__main__":
    main()