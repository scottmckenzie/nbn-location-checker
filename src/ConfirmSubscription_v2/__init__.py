import azure.durable_functions as df
import azure.functions as func
import json
import logging
import shared_code.cosmos as cosmos
from shared_code.utils import http_response


API_VERSION = 2

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    functionName = f"'Functions.ConfirmSubscription_v{API_VERSION}'"
    message = 'subscription not found'

    # validate instance_id
    instance_id = req.route_params.get('instance_id')
    if not instance_id:
        logging.warning(f'{functionName} No instance_id')
        return http_response(status_code=404, message=message)
    
    # validate status of orchestration
    client = df.DurableOrchestrationClient(starter)
    status = await client.get_status(instance_id, show_input=True)
    if not status:
        logging.warning(f'{functionName} Invalid instance_id: {instance_id}')
        return http_response(status_code=404, message=message)
    if status.runtime_status.value != 'Running':
        logging.warning(
            f'{functionName} Instance_id {instance_id} is not running')
        return http_response(status_code=404, message=message)
    
    # add subscription to the database
    input = json.loads(status.input_)
    sub = {
        'id': input['location_id'],
        'email': input['email']
    }
    logging.info(f'{functionName} adding subscription: {sub}')
    cosmos.upsert_subscription(sub)

    # fire ConfirmSubscriptionEvent
    await client.raise_event(
        instance_id, f'ConfirmSubscription_v{API_VERSION}')
    return func.HttpResponse('Success! you are subscribed')
