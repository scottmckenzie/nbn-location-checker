import azure.functions as func
import json
import logging
import typing
from shared_code.table import AzureTableClient


def main(msg: func.QueueMessage, msgout: func.Out[typing.List[str]]) -> None:
    functionName = "'Function.MigrateAllSubsciptions'"
    msg = msg.get_body().decode('utf-8')
    logging.info(f'{functionName} queue trigger function processed a ' +
                 f'queue item: {msg}')
    if not "start-migration" == msg:
        return
    messages = []
    filter = f"RowKey ne '.'"
    with AzureTableClient.get() as table:
        # iterate over all subscriptions
        for sub in table.query_entities(filter):
            msg = {
                "id": sub['PartitionKey'],
                "email": sub['RowKey']
            }
            messages.append(json.dumps(msg))
    if messages:
        msgout.set(messages)
        logging.info(f'{functionName} Added {len(messages)} message(s) to the queue')
    else:
        logging.info(f'{functionName} No messages add to the queue')
