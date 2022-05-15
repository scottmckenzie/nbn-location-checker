import azure.functions as func
import json
import logging
import mimetypes
from shared_code.table import AzureTableClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')


    locations = 0
    subscribers = []
    subscriptions = 0
    with AzureTableClient.get() as table:
        # iterate over all locations
        filter = f"RowKey eq '.'"
        for location in table.query_entities(filter):
            locations += 1
            partition_key = location['PartitionKey']
            filter = f"PartitionKey eq '{partition_key}' and RowKey ne '.'"
            # iterate over all subscribers to this location
            for subscriber in table.query_entities(filter):
                subscriptions += 1
                if subscriber['RowKey'] not in subscribers:
                    subscribers.append(subscriber['RowKey'])
    data = {
        'locations': locations,
        'subscribers': len(subscribers),
        'subscriptions': subscriptions
    }
    mimetype = mimetypes.types_map['.json']
    return func.HttpResponse(json.dumps(data), mimetype=mimetype)
