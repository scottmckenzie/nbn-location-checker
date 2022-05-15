import azure.durable_functions as df
import azure.functions as func
import logging
from shared_code.nbn import get_location_and_store, valid_location
from shared_code.utils import http_response, valid_email
from urllib.parse import parse_qs

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    fn = '[Subscribe.httpTrigger]'
    logging.info(f'{fn} processing a {req.method} request')
    
    email, location = get_params(req)
    
    # return index page if GET request or paramters are absent
    if req.method == 'GET' or not location or not email:
        logging.info(f'{fn} serving index.html')
        return http_response(200)
    
    # return 400 for invalid email or location
    message = None
    if not valid_email(email):
        message = f'Invalid email address: {email}'
    if not valid_location(location):
        message = f'Invalid location ID: {location}'
    if message:
        logging.info(f'{fn} {message}')
        return http_response(400, message)
    
    # return 404 for invalid location
    data = get_location_and_store(location)
    if data is None:
        message = f'Location {location} not found'
        logging.info(f'{fn} {message}')
        return http_response(404, message)
    
    # return 400 if connected via FTTB, FTTP, HFC
    if data.get('techType') in ['FTTB', 'FTTP', 'HFC']:
        message = f'{location} connected via {data.get("techType")}'
        logging.info(f'{fn} {message}')
        return http_response(400, message)
    
    # return 400 if already eligilbe for FTTP upgrade
    if data.get('patChangeStatus') == True:
        message = f'{location} eligible for FTTP upgrade since {data.get("patChangeDate")}'
        logging.info(f'{fn} {message}')
        return http_response(400, message)
    
    # start durable function for email validation
    data['email'] = email
    data['url'] = req.url
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new("EmailVerificationOrchestrator", None, data)
    logging.info(f'{fn} Started orchestration with ID {instance_id}')
    return func.HttpResponse('Check your email for more info.')

def get_params(req: func.HttpRequest) -> tuple:
    email = None
    location = None
    accepted_content_type = 'application/x-www-form-urlencoded'
    content_type = req.headers.get('content-type')
    # parameters can only be passed in POST
    if req.method == 'POST' and accepted_content_type == content_type:
        body = req.get_body().decode('utf-8')
        params = parse_qs(body)
        email = params.get('email')[0]
        location = params.get('location')[0]
    return email, location
