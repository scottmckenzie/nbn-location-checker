import logging
import os
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from types import SimpleNamespace

# initialise CosmosClient and containers
_m = SimpleNamespace()
_m.client = CosmosClient.from_connection_string(
    os.getenv(u'AzureCosmosDBConnectionString'))
_m.db = _m.client.get_database_client('cosmos-nbn')
_m.locations = _m.db.get_container_client('locations')
_m.stats = _m.db.get_container_client('stats')
_m.subs = _m.db.get_container_client('subs')

async def delete_subscription(subscription: dict) -> None:
    await _m.subs.delete_item(subscription['id'], subscription['id'])

async def get_all_csas() -> list:
    result = []
    async for item in _m.subs.read_all_items():
        result.append(item)
    return result

async def get_location(csa_id: str, location_id: str) -> dict:
    location = await _m.locations.read_item(location_id, csa_id)
    return location

async def get_alt_reason_code(csa_id: str, location_id: str) -> str:
    result = ''
    location = await get_location(csa_id, location_id)
    if location:
        result = location['addressDetail']['altReasonCode']
    return result

async def upsert_location(location: dict) -> None:
    await _m.locations.upsert_item(location)
