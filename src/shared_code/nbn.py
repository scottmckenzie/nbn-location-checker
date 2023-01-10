import aiohttp
import logging
import re
import requests
from types import SimpleNamespace
from .table import AzureTableClient


_m = SimpleNamespace()
# compile regular expression
_m.pattern = re.compile('^LOC\d{12}$')
# initialise ClientSession
_m.session = aiohttp.ClientSession(
    base_url='https://places.nbnco.net.au',
    headers={'referer': 'https://www.nbnco.com.au/'})

# get location from NBN API
async def get_location_async(location_id: str) -> dict:
    functionName = "'nbn.get_location_async'"
    logging.info(f'{functionName} Requesting location {location_id}')
    location = None
    try:
        async with _m.session.get(f'/places/v2/details/{location_id}') as resp:
            if resp.ok:
                location = await(resp.json())
            else:
                logging.error(f'{functionName} Request for {location_id} ' +
                    f'returned HTTP status {resp.status}')
    except BaseException as err:
        logging.error(f'Unexpected {err=}, {type(err)=}')
    if location:
        # configure for cosmos db
        location.pop('timestamp')
        location['csa_id'] = location['servingArea']['csaId']
        location['id'] = location_id
    return location

# get location from NBN API
def get_location(location_id: str) -> dict:
    functionName = "'nbn.get_location'"
    url = f'https://places.nbnco.net.au/places/v2/details/{location_id}'
    headers = {'referer': 'https://www.nbnco.com.au/'}
    logging.info(f'{functionName} requesting location {location_id}')
    response = requests.get(url, headers=headers)
    if not response.ok:
        logging.error(f'{functionName} request for {location_id} returned ' +
            f'HTTP status {response.status_code}')
        return None
    location = response.json()
    # configure for cosmos db
    location.pop('timestamp')
    location['csa_id'] = location['servingArea']['csaId']
    location['id'] = location_id
    return location

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
        return 'FTTP may be available at your location soon'
    if code == 'FTTP_SA':
        return 'Good news! You may be able to upgrade to FTTP'
    logging.error(f'{fn} Unknown code {code}')
    return 'Unknown status code :('

# store the location in the table
def upsert_location(location):
    with AzureTableClient.get() as table:
        table.upsert_entity(location)

def valid_location(location_id: str) -> bool:
    if re.fullmatch(_m.pattern, location_id):
        return True
    return False
