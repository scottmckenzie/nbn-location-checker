import azure.functions as func
import logging
from shared_code.nbn import get_location
from shared_code.cosmos import upsert_location


def main(msg: func.QueueMessage) -> None:
    functionName = "'Functions.MigrateOneLocation'"
    msg = msg.get_body().decode('utf-8')
    logging.info(f'{functionName} queue trigger function processed a ' +
                 f'queue item: {msg}')
    location = get_location(msg)
    if not location:
        return
    upsert_location(location)
