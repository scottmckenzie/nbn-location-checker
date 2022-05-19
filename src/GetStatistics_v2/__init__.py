import azure.functions as func
import json
import mimetypes
import shared_code.cosmos as cosmos


API_VERSION = 2

def main(req: func.HttpRequest) -> func.HttpResponse:
    data = {
        'locations': cosmos.get_location_count(),
        'subscribers': cosmos.get_subscriber_count(),
        'subscriptions': cosmos.get_subscription_count()
    }
    mimetype = mimetypes.types_map['.json']
    return func.HttpResponse(json.dumps(data), mimetype=mimetype)
