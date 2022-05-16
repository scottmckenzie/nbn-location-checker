import os
from azure.cosmos.cosmos_client import CosmosClient


DATABASE_ID = 'cosmos-nbn'
LOCATIONS = 'locations'
SUBS = 'subs'

def get_cosmos_client() -> CosmosClient:
    conn_str = os.environ.get(u'AzureCosmosDBConnectionString')
    return CosmosClient.from_connection_string(conn_str)

def get_csa_id(location_id: str) -> str:
    client = get_cosmos_client()
    db = client.get_database_client(DATABASE_ID)
    container = db.get_container_client(LOCATIONS)
    query = (f"SELECT value c.servingArea.csaId FROM c " +
             f"WHERE c.addressDetail.id = '{location_id}'")
    for item in container.query_items(query, enable_cross_partition_query=True):
        return item
    return None
