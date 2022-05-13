import azure.durable_functions as df
import azure.functions as func
import json
import logging
import mimetypes
from shared_code.nbn import upsert_location
from shared_code.utils import get_html_file


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    fn = '[ConfirmSubscription.httpTrigger]'

    # validate instance_id
    instance_id = req.route_params.get('instance_id')
    client = df.DurableOrchestrationClient(starter)
    status = await client.get_status(instance_id, show_input=True)
    if status.runtime_status.value != 'Running':
        logging.warning(f'{fn} received an invalid instance_id: {instance_id}')
        body = get_html_file('400.html').format('id')
        mimetype = mimetypes.types_map['.html']
        return func.HttpResponse(body, status_code=400, mimetype=mimetype)
    
    # add subscription to Azure tables
    input = json.loads(status.input_)
    entity = {
        'PartitionKey': input['PartitionKey'],
        'RowKey': input['email']
    }
    logging.info(f'{fn} adding subscription: {entity}')
    upsert_location(entity)
    await client.raise_event(instance_id, 'ConfirmSubscriptionEvent')
    return func.HttpResponse('Success! you are subcribed')
