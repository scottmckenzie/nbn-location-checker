import azure.functions as func
import datetime
import logging
import os
from azure.data.tables import TableServiceClient


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    
    connection_string = os.environ.get(u'AzureWebJobsStorage')
    logging.info(f'Using connection string {connection_string}')
    service_client = TableServiceClient.from_connection_string(connection_string)
    table_names = {'locations', 'users'}
    for table_name in table_names:
        tc = service_client.create_table_if_not_exists(table_name)

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
