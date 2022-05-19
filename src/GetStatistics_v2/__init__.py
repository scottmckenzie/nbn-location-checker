import azure.functions as func
import json
import logging
import mimetypes
from shared_code.cosmos import get_database_client, get_location_count
from shared_code.cosmos import get_subscriber_count, get_subscription_count


API_VERSION = 2

def main(req: func.HttpRequest) -> func.HttpResponse:
    functionName = f"'Functions.GetStatistics_v{API_VERSION}'"
    logging.info(f'{functionName} httpTrigger function processed a request.')

    db = get_database_client()
    location_count = get_location_count(db)
    subscriber_count = get_subscriber_count(db)
    subscription_count = get_subscription_count(db)

    data = {
        'locations': location_count,
        'subscribers': subscriber_count,
        'subscriptions': subscription_count
    }
    mimetype = mimetypes.types_map['.json']
    return func.HttpResponse(json.dumps(data), mimetype=mimetype)
