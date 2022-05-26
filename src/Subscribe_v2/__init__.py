import azure.durable_functions as df
import azure.functions as func
import logging
import shared_code.cosmos as cosmos
import shared_code.nbn as nbn
import shared_code.utils as utils
from urllib.parse import parse_qs


API_VERSION = 2

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    functionName = f"'Functions.Subscribe_v{API_VERSION}'"
    logging.info(
        f'{functionName} httpTrigger processing a {req.method} request')
    
    email, location_id = get_params(req)
    
    # return index page if GET request or paramters are absent
    if req.method == 'GET' or not location_id or not email:
        return utils.http_response(200)
    
    # return 400 for invalid email or location_id
    message = None
    if not utils.valid_email(email):
        message = f'Invalid email address: {email}'
    if not nbn.valid_location(location_id):
        message = f'Invalid location ID: {location_id}'
    if message:
        logging.info(f'{functionName} {message}')
        return utils.http_response(400, message)
    
    # return 404 for invalid location_id
    location = await nbn.get_location_async(location_id)
    if location is None:
        message = f'Location {location_id} not found'
        logging.info(f'{functionName} {message}')
        return utils.http_response(404, message)
    cosmos.upsert_location(location)
    
    # return 400 if connected via FTTB, FTTP, HFC
    techtype = location['addressDetail']['techType']
    if techtype in ['FTTB', 'FTTP', 'HFC']:
        message = (f'{location_id} Connected via {techtype} ' +
                   '(not eligible for upgrade)')
        logging.info(f'{functionName} {message}')
        return utils.http_response(400, message)
    
    # return 400 if already eligible for FTTP upgrade
    if location['addressDetail'].get('patChangeStatus') == True:
        message = f'{location_id} Eligible for FTTP upgrade'
        change_date = location["addressDetail"].get("patChangeDate")
        if change_date:
            message += f' since {change_date}'
        logging.info(f'{functionName} {message}')
        return utils.http_response(400, message)
    
    # start durable function for email validation
    durable_input = {
        'csa_id': location['csa_id'],
        'email': email,
        'formattedAddress': location['addressDetail']['formattedAddress'],
        'location_id': location_id,
        'url': req.url,
    }
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new(
        f"Orchestrator_v{API_VERSION}", client_input=durable_input)
    logging.info(
        f'{functionName} Started orchestration with ID {instance_id}')
    return func.HttpResponse('Check your email for more info.')

def get_params(req: func.HttpRequest) -> tuple:
    email = None
    location_id = None
    accepted_content_type = 'application/x-www-form-urlencoded'
    content_type = req.headers.get('content-type')
    # parameters can only be passed in POST
    if req.method == 'POST' and accepted_content_type == content_type:
        body = req.get_body().decode('utf-8')
        params = parse_qs(body)
        email = params.get('email')[0]
        location_id = params.get('location')[0]
    return email, location_id
