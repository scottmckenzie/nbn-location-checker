import azure.functions as func
import json
import logging
from shared_code.cosmos import get_csa_id


def main(msg: func.QueueMessage, doc: func.Out[func.Document]) -> None:
    functionName = "'Functions.MigrateOneSubscription'"
    logging.info(f'{functionName} queue trigger function processed a ' +
                 f'queue item: %s', msg.get_body().decode('utf-8'))
    sub = json.loads(msg.get_body().decode('utf-8'))
    csa_id = get_csa_id(sub['location_id'])
    if not csa_id:
        msg = f'{functionName} CSA not found for {sub["location_id"]}'
        logging.error(msg)
        return
    sub['csa_id'] = csa_id
    doc.set(func.Document.from_dict(sub))
