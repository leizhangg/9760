import os
from sodapy import Socrata
import sys
import argparse
# connect ES with requests module

import requests
from requests.auth import HTTPBasicAuth

# data we are pulling, authentication aspects 
DATASET_ID=os.environ["DATASET_ID"]
APP_TOKEN=os.environ["APP_TOKEN"]
ES_HOST=os.environ["ES_HOST"]
INDEX_NAME=os.environ["INDEX_NAME"]
ES_USERNAME=os.environ["ES_USERNAME"]
ES_PASSWORD=os.environ["ES_PASSWORD"]

parse = argparse.ArgumentParser(description = "Process data from OPCV")
parse.add_argument('--page_size', type = int, help='how many rows to get per page',required = True)
parse.add_argument('--num_pages', type = int, help='how many pages to get in total')
args = parse.parse_args(sys.argv[1:])
print(args)
# build index
if __name__ == '__main__':
    try:
        resp =requests.put(
              f"{ES_HOST}/{INDEX_NAME}",
              auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD),
              json={
                  "settings":{
                      "number_of_shards":3,
                      "number_of_replicas":1
                  },
                   "mappings":{
                      "properties":{
                                "plate":{"type":"keyword"},
                                "state":{"type":"keyword"},
                                "license_type":{"type":"keyword"},
                                "summons_number":{"type":"keyword"},
                                "issue_date":{"type":"date","format":"MM/dd/yyyy"},
                               # "violation_time":{"type":"keyword"},
                                "violation":{"type":"keyword"},
                                #"judgment_entry_date":{"type":"keyword"},
                                "fine_amount":{"type":"float"},
                                "penalty_amount":{"type":"float"},
                                "interest_amount":{"type":"float"},
                                "reduction_amount":{"type":"float"},
                                "payment_amount":{"type":"float"},
                                "amount_due":{"type":"float"},
                                "precinct":{"type":"keyword"},
                                "county":{"type":"keyword"},
                                "issuing_agency":{"type":"keyword"},
                                #"violation_status":{"type":"keyword"},
                                }
                        }
                    }
                )
        resp.raise_for_status()
    except Exception as e:
        print("Index already exists!")
            
# connect to data source and upload it to ES
    client = Socrata(
         "data.cityofnewyork.us",
            APP_TOKEN,
        )
    rows = client.get(DATASET_ID, limit=args.page_size)
    for i, row in enumerate(rows):
        try:
            es_row = {}
            es_row["plate"] = row["plate"]
            es_row["state"] = row["state"]
            es_row["license_type"] = row["license_type"]
            es_row["summons_number"] = row["summons_number"]
            es_row["issue_date"] = row["issue_date"]
            #es_row["violation_time"] = row["violation_time"]
            es_row["violation"] = row["violation"]
            #es_row["judgment_entry_date"] = row["judgment_entry_date"]
            es_row["fine_amount"] = float(row["fine_amount"])
            es_row["penalty_amount"] = float(row["penalty_amount"])
            es_row["interest_amount"] = float(row["interest_amount"])
            es_row["reduction_amount"] = float(row["reduction_amount"])
            es_row["payment_amount"] = float(row["payment_amount"])
            es_row["amount_due"] = float(row["amount_due"])
            es_row["precinct"] = row["precinct"]
            es_row["county"] = row["county"]
            es_row["issuing_agency"] = row["issuing_agency"]
            #es_row["violation_status"] = row["violation_status"]
            
        except Exception as e:
            print(f"Skipping because of failure: {e}")

#upload to ES by creating a doc
        try:
            resp = requests.post(
                f"{ES_HOST}/{INDEX_NAME}/_doc",
                auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD),
                json=es_row,
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"Failed to upload to elasticsearch! {e}")
            
            
#DATASET_ID = "nc67-uf89"
#APP_TOKEN = "YLPWKFq3ghgRKnDktgcxbuWwb"
#INDEX_NAME = "opcv6"

#ES_HOST = "https://search-sta9760-t27zq5po3psy3jagr7vtqu7p2e.us-east-1.es.amazonaws.com"
#ES_USERNAME = "sta9760"
#ES_PASSWORD = "121@Baxter"


        
        
        