import os
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from types import SimpleNamespace


# initialise CosmosClient and containers
_m = SimpleNamespace()
_m.client = CosmosClient.from_connection_string(
    os.getenv(u'AzureCosmosDBConnectionString'))
_m.db = _m.client.get_database_client('cosmos-nbn')
_m.locations = _m.db.get_container_client('locations')
_m.subs = _m.db.get_container_client('subs')

def create_subscription(subscription: dict) -> None:
    _m.subs.create_item(subscription)

def get_all_locations() -> list:
    return list(_m.locations.read_all_items())

def get_all_subscriptions() -> list:
    return list(_m.subs.read_all_items())

def get_alt_reason_code(csa_id: str, location_id: str) -> str:
    query = (f'SELECT VALUE c.addressDetail.altReasonCode FROM c ' +
             f"WHERE c.csa_id='{csa_id}' and c.id='{location_id}'")
    return next(
        _m.locations.query_items(query, enable_cross_partition_query=True))

def get_csa_id(location_id: str) -> str:
    query = (f"SELECT VALUE c.csa_id FROM c WHERE c.id='{location_id}'")
    return next(
        _m.locations.query_items(query, enable_cross_partition_query=True))

def get_location(location_id: str) -> dict:
    query = f"SELECT * FROM c WHERE c.id='{location_id}'"
    return next(
        _m.locations.query_items(query, enable_cross_partition_query=True))

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

def get_subscribers(location_id: str) -> list:
    query = f"SELECT VALUE c.email FROM c WHERE c.id='{location_id}'"
    return list(
        _m.subs.query_items(query, enable_cross_partition_query=True))

def get_subscription(location_id: str) -> dict:
    try:
        return _m.subs.read_item(location_id, location_id)
    except CosmosHttpResponseError:
        return None

def get_subscription_count() -> int:
    query = 'SELECT VALUE COUNT(1) FROM c'
    return next(
        _m.subs.query_items(query, enable_cross_partition_query=True))

def get_subscriptions() -> list:
    query = 'SELECT c.id, c.csa_id, c.subscribers FROM c'
    return list(_m.subs.query_items(query, enable_cross_partition_query=True))

def replce_subscription(subscription: dict) -> None:
    _m.subs.replace_item(subscription['id'], subscription)

def upsert_location(location: dict) -> None:
    _m.locations.upsert_item(location)
