import azure.functions as func
import json
import logging
import mimetypes
from shared_code.cosmos import get_location_count, get_subscriber_count, get_subscription_count


API_VERSION = 2

def main(req: func.HttpRequest) -> func.HttpResponse:
    functionName = f"'Functions.GetStatistics_v{API_VERSION}'"
    logging.info(f'{functionName} httpTrigger function processed a request.')

    data = {
        'locations': get_location_count(),
        'subscribers': get_subscriber_count(),
        'subscriptions': get_subscription_count()
    }
    mimetype = mimetypes.types_map['.json']
    return func.HttpResponse(json.dumps(data), mimetype=mimetype)
