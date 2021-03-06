import azure.functions as func
import logging
import typing
from shared_code.table import AzureTableClient


def main(msg: func.QueueMessage, msgout: func.Out[typing.List[str]]) -> None:
    functionName = "'Function.MigrateAllLocations'"
    msg = msg.get_body().decode('utf-8')
    logging.info(f'{functionName} queue trigger function processed a ' +
                 f'queue item: {msg}')
    if not "start-migration" == msg:
        return
    messages = []
    filter = f"RowKey eq '.'"
    with AzureTableClient.get() as table:
        # iterate over all locations
        for location in table.query_entities(filter):
            messages.append(location['PartitionKey'])
    if messages:
        msgout.set(messages)
        logging.info(f'{functionName} Added {len(messages)} message(s) to the queue')
    else:
        logging.info(f'{functionName} No messages add to the queue')
