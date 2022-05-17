import azure.functions as func
import json
import logging
from shared_code.cosmos import upsert_subscription


def main(msg: func.QueueMessage) -> None:
    functionName = "'Functions.MigrateOneSubscription'"
    msg = msg.get_body().decode('utf-8')
    logging.info(f'{functionName} queue trigger function processed a ' +
                 f'queue item: {msg}')
    sub = json.loads(msg)
    upsert_subscription(sub)
