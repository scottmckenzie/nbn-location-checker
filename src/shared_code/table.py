import os
from azure.data.tables import TableClient


class AzureTableClient():

    def __init__(self) -> None:
        pass

    @classmethod
    def get(cls):
        conn_str = os.environ.get(u'AzureWebJobsStorage')
        return TableClient.from_connection_string(conn_str=conn_str,
                                                  table_name='locations')
