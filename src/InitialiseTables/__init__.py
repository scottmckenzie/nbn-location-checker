import azure.functions as func
import datetime
import logging
import os
from azure.data.tables import TableServiceClient


def main(mytimer: func.TimerRequest) -> None:
    fn = '[InitialiseTables.timerTrigger]'

    if mytimer.past_due:
        logging.info(f'{fn} The timer is past due!')
    
    logging.info(f'{fn} creating tables')
    connection_string = os.environ.get(u'AzureWebJobsStorage')
    service_client = TableServiceClient.from_connection_string(connection_string)
    table_names = {'locations', 'users'}
    for table_name in table_names:
        tc = service_client.create_table_if_not_exists(table_name)
    
    logging.info(f'{fn} table creation complete')
