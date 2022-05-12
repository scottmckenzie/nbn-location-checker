import re
import requests
from .table import AzureTableClient


def get_location(location: str):
    entity = from_nbn_api(location)
    if entity:
        upsert_location(entity)
    return entity

def get_location_from_table_storage(location: str):
    # get location from storage
    entity = None
    my_filter = f"PartitionKey eq '{location}' and RowKey eq '.'"
    with AzureTableClient.get() as table:
        entities = table.query_entities(my_filter)
        for entity in entities:
            pass
    return entity

def from_nbn_api(location: str):
    # get location from NBN
    url = f'https://places.nbnco.net.au/places/v2/details/{location}'
    headers = {'referer': 'https://www.nbnco.com.au/'}
    r = requests.get(url=url, headers=headers)
    if not r.ok:
        return None
    
    entity = r.json()['addressDetail']
    entity['PartitionKey'] = entity.pop('id')
    entity['RowKey'] = '.'
    return entity

def merge_entities(to_send, entity):
    r = {}
    for name, value in to_send.items():
        if to_send.get(name) != entity.get(name):
            r[name] = value
    if r:
        r['PartitionKey'] = to_send['PartitionKey']
        r['RowKey'] = '.'
    return r

# define our own upsert as the SDK one updates the etag even when no data changes
def upsert_location(location):
    # merge with enitity from table storage if it exists
    entity = get_location_from_table_storage(location['PartitionKey'])
    if entity:
        location = merge_entities(location, entity)
    
    # upsert new/updated location
    if location:
        with AzureTableClient.get() as table:
            location = table.upsert_entity(location)

def valid_location(location: str) -> bool:
    if re.fullmatch('LOC\d{12}', location):
        return True
    return False
