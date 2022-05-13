import azure.durable_functions as df
import azure.functions as func
import logging
from shared_code.nbn import get_location_and_store, valid_location
from shared_code.utils import http_response, valid_email

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    fn = '[Subscribe.httpTrigger]'
    logging.info(f'{fn} processing a {req.method} request')
    
    email = req.params.get('email')
    location = req.params.get('location')
    
    # return index page if both paramters are absent
    if not location and not email:
        logging.info(f'{fn} serving index.html')
        return http_response(200)
    
    # return 400 for invalid email or location
    message = None
    if not valid_email(email):
        message = 'Invalid email address format'
    if not valid_location(location):
        message = 'Invalid location ID'
    if message:
        message = f'{location} not found'
        logging.info(f'{fn} {message}')
        return http_response(400, message)
    
    # return 404 for invalid location
    data = get_location_and_store(location)
    if data is None:
        message = f'{location} not found'
        logging.info(f'{fn} {message}')
        return http_response(404)
    
    # return 400 if connect via FTTP or HFC
    if data.get('techType') == 'FTTP' or data.get('techType') == 'HFC':
        message = f'{location} connected via data.get("techType")'
        logging.info(f'{fn} {message}')
        return http_response(400, message)

    # return 400 if already eliglbe for FTTP upgrade
    if data.get('patChangeStatus') == True:
        message = f'{location} eligible for FTTP upgrade since {data.get("patChangeDate")}'
        logging.info(f'{fn} {message}')
        return http_response(400, message)

    # start durable function for email validation
    data['email'] = email
    data['url'] = req.url
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new("EmailVerificationOrchestrator", None, data)
    logging.info(f"{fn} Started orchestration with ID '{instance_id}'")
    return func.HttpResponse(f"Check your email for more info.")
