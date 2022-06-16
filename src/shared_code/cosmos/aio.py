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

async def get_all_csas() -> list:
    result = []
    async for item in _m.subs.read_all_items():
        result.append(item)
    return result

