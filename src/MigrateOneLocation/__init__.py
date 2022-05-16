import azure.functions as func
import logging
from shared_code.nbn import get_location_from_nbn_api


def main(msg: func.QueueMessage, doc: func.Out[func.Document]) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))
    location_id = msg.get_body().decode('utf-8')
    location = get_location_from_nbn_api(location_id)
    if not location:
        return
    location.pop('timestamp')
    doc.set(func.Document.from_dict(location))
