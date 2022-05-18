import azure.durable_functions as df
import azure.functions as func
import logging
from shared_code.nbn import get_location, valid_location
from shared_code.utils import http_response, valid_email
from urllib.parse import parse_qs


API_VERSION = 2

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    functionName = f"'Functions.Subscribe_v{API_VERSION}'"
    logging.info(
        f'{functionName} httpTrigger processing a {req.method} request')
    
    email, location_id = get_params(req)
    
    # return index page if GET request or paramters are absent
    if req.method == 'GET' or not location_id or not email:
        logging.info(f'{functionName} serving index.html')
        return http_response(200)
    
    # return 400 for invalid email or location_id
    message = None
    if not valid_email(email):
        message = f'Invalid email address: {email}'
    if not valid_location(location_id):
        message = f'Invalid location ID: {location_id}'
    if message:
        logging.info(f'{functionName} {message}')
        return http_response(400, message)
    
    # return 404 for invalid location_id
    location = get_location(location_id)
    if location is None:
        message = f'Location {location_id} not found'
        logging.info(f'{functionName} {message}')
        return http_response(404, message)
    
    # return 400 if connected via FTTB, FTTP, HFC
    if location.get('techType') in ['FTTB', 'FTTP', 'HFC']:
        message = f'{location_id} connected via {location["techType"]}'
        logging.info(f'{functionName} {message}')
        return http_response(400, message)
    
    # return 400 if already eligilbe for FTTP upgrade
    if location.get('patChangeStatus') == True:
        message = (f'{location_id} eligible for FTTP upgrade since ' +
                   f'{location.get("patChangeDate")}')
        logging.info(f'{functionName} {message}')
        return http_response(400, message)
    
    # start durable function for email validation
    durable_input = {
        "email": email,
        "location_id": location_id,
        "location": location,
        "url": req.url,
    }
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new(
        f"Orchestrator_v{API_VERSION}", None, durable_input)
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
