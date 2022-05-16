import logging
import re
import requests
from .table import AzureTableClient


def get_location_and_store(location: str):
    entity = get_location_from_nbn_api(location)
    if entity:
        upsert_location(entity)
    return entity

# get location from NBN API
def get_location(location_id: str):
    fn = '[get_location]'
    url = f'https://places.nbnco.net.au/places/v2/details/{location}'
    headers = {'referer': 'https://www.nbnco.com.au/'}
    logging.info(f'{fn} requesting location {location_id}')
    response = requests.get(url=url, headers=headers)
    if not response.ok:
        logging.error(f'{fn} request for {location_id} returned HTTP ' +
            f'status {response.status_code}')
        return None
    return response.json()

def get_location_from_nbn_api(location: str):
    fn = '[get_location_from_nbn_api]'
    url = f'https://places.nbnco.net.au/places/v2/details/{location}'
    headers = {'referer': 'https://www.nbnco.com.au/'}
    logging.info(f'{fn} requesting location {location}')
    response = requests.get(url=url, headers=headers)
    if not response.ok:
        logging.error(
            f'{fn} request for {location} returned HTTP status {response.status_code}')
        return None
    
    entity = response.json()['addressDetail']
    entity['PartitionKey'] = entity.pop('id')
    entity['RowKey'] = '.'
    return entity

def get_nbn_status(code: str) -> str:
    fn = '[get_nbn_status]'
    if code == 'FTTP_NA':
        return 'Good news! You may be able to upgrade to FTTP soon'
    if code == 'FTTP_SA':
        return 'Good news! You may be able to upgrade to FTTP'
    logging.error(f'{fn} Unknown code {code}')
    return 'Unknown status code :('

def get_location(location_id: str):
    fn = '[get_location]'
    url = f'https://places.nbnco.net.au/places/v2/details/{location}'
    headers = {'referer': 'https://www.nbnco.com.au/'}
    logging.info(f'{fn} requesting location {location_id}')
    response = requests.get(url=url, headers=headers)
    if not response.ok:
        logging.error(f'{fn} request for {location_id} returned HTTP ' +
            f'status {response.status_code}')
        return None
    return response.json()

# store the location in the table
def upsert_location(location):
    with AzureTableClient.get() as table:
        table.upsert_entity(location)

def valid_location(location: str) -> bool:
    if re.fullmatch('LOC\d{12}', location):
        return True
    return False
