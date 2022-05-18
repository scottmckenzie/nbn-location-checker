import os
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos import ContainerProxy


DATABASE_ID = 'cosmos-nbn'
LOCATIONS = 'locations'
SUBS = 'subs'

def get_all_locations() -> list:
    container = get_container_client(LOCATIONS)
    return list(container.read_all_items())
    
def get_container_client(container: str) -> ContainerProxy:
    conn_str = os.environ.get(u'AzureCosmosDBConnectionString')
    client = CosmosClient.from_connection_string(conn_str)
    db = client.get_database_client(DATABASE_ID)
    return db.get_container_client(container)

def get_location_count() -> int:
    container = get_container_client(LOCATIONS)
    query = 'SELECT VALUE COUNT(1) FROM c'
    return next(
        container.query_items(query, enable_cross_partition_query=True))

def get_location_subscribers(location_id: str) -> list:
    container = get_container_client(SUBS)
    query = f'SELECT * from c WHERE c.id = "{location_id}"'
    return list(container.query_items(query))

def get_subscriber_count() -> int:
    container = get_container_client(SUBS)
    query = ('SELECT VALUE COUNT(1) FROM c JOIN ' +
            '(SELECT DISTINCT c.email FROM c)')
    return next(
        container.query_items(query, enable_cross_partition_query=True))

def get_subscription_count() -> int:
    container = get_container_client(SUBS)
    query = 'SELECT VALUE COUNT(1) FROM c'
    return next(
        container.query_items(query, enable_cross_partition_query=True))

def upsert_location(location: dict) -> None:
    container = get_container_client(LOCATIONS)
    response = container.upsert_item(location)


def upsert_subscription(sub: dict) -> None:
    container = get_container_client(SUBS)
    response = container.upsert_item(sub)
