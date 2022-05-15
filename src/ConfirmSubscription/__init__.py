import azure.durable_functions as df
import azure.functions as func
import json
import logging
import mimetypes
from shared_code.nbn import upsert_location
from shared_code.utils import get_html_file, http_response


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    fn = '[ConfirmSubscription.httpTrigger]'
    message = 'subscription not found'

    # validate instance_id
    instance_id = req.route_params.get('instance_id')
    if not instance_id:
        logging.warning(f'{fn} no instance_id')
        return http_response(status_code=404, message=message)
    client = df.DurableOrchestrationClient(starter)
    status = await client.get_status(instance_id, show_input=True)
    if not status or status.runtime_status.value != 'Running':
        logging.warning(f'{fn} invalid instance_id: {instance_id}')
        return http_response(status_code=404, message=message)
    
    # add subscription to Azure tables
    input = json.loads(status.input_)
    entity = {
        'PartitionKey': input['PartitionKey'],
        'RowKey': input['email']
    }
    logging.info(f'{fn} adding subscription: {entity}')
    upsert_location(entity)
    await client.raise_event(instance_id, 'ConfirmSubscriptionEvent')
    return func.HttpResponse('Success! you are subscribed')
