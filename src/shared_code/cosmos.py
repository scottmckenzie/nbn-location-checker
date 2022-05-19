import os
from azure.cosmos.cosmos_client import CosmosClient
from types import SimpleNamespace


# initialise CosmosClient and containers
_m = SimpleNamespace()
_m.client = CosmosClient.from_connection_string(
    os.getenv(u'AzureCosmosDBConnectionString'))
_m.db = _m.client.get_database_client('cosmos-nbn')
_m.locations = _m.db.get_container_client('locations')
_m.subs = _m.db.get_container_client('subs')

def get_all_locations() -> list:
    return list(_m.locations.read_all_items())
    
def get_location_count() -> int:
    query = 'SELECT VALUE COUNT(1) FROM c'
    return next(
        _m.locations.query_items(query, enable_cross_partition_query=True))

def get_location_subscribers(location_id: str) -> list:
    query = f'SELECT * from c WHERE c.id = "{location_id}"'
    return list(_m.subs.query_items(query))

def get_subscriber_count() -> int:
    query = 'SELECT DISTINCT VALUE c.email FROM c'
    subscribers = list(
        _m.subs.query_items(query, enable_cross_partition_query=True))
    return len(subscribers)

def get_subscription_count() -> int:
    query = 'SELECT VALUE COUNT(1) FROM c'
    return next(
        _m.subs.query_items(query, enable_cross_partition_query=True))

def upsert_location(location: dict) -> None:
    _m.locations.upsert_item(location)

def upsert_subscription(sub: dict) -> None:
    _m.subs.upsert_item(sub)
