import azure.functions as func
import logging
import typing
from shared_code.table import AzureTableClient


def main(msg: func.QueueMessage, msg_out: func.Out[typing.List[str]]) -> None:
    fn = "'Function.MigrateAllLocations'"
    logging.info(f'{fn} queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))
    if not "start-migration" == msg.get_body().decode('utf-8'):
        return
    messages = []
    filter = f"RowKey eq '.'"
    with AzureTableClient.get() as table:
        # iterate over all locations
        for location in table.query_entities(filter):
            messages.append(location['PartitionKey'])
    if messages:
        msg.set(messages)
        logging.info(f'{fn} Added {len(messages)} message(s) to the queue')
    else:
        logging.info(f'{fn} No messages add to the queue')
