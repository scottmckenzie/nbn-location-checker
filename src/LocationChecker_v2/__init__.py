import azure.functions as func
import json
import logging
from shared_code import cosmos, nbn


API_VERSION = 2

# msg: storage queue message that triggered the function
# message: SendGrid message
async def main(msg: func.QueueMessage, message: func.Out[str]) -> None:
    functionName = f"'Functions.LocationChecker_v{API_VERSION}'"

    msg = msg.get_body().decode('utf-8')
    logging.info(f'{functionName} Processing queue item: {msg}')
    
    # convert json msg string to a dict
    sub = json.loads(msg)
    location_id = sub['id']
    l1altReason = cosmos.get_alt_reason_code(sub['csa_id'], location_id)

    l2 = await nbn.get_location_async(location_id)
    if l2 is None:
        raise Exception(f'Failed to get location {location_id}')
    if l2['addressDetail']['techType'] == 'FTTP':
        #TODO send email advising of upgrade and sub removal
        # delete subscription
        cosmos.delete_subscription(sub)
    else:
        l2altReason = l2['addressDetail']['altReasonCode']
        
        # has altReasonCode code changed?
        if l1altReason == l2altReason:
            return
        logging.info(f'{functionName} Location {location_id} has changed from '
            f'{l1altReason} to {l2altReason}')
        
        # construct email message(s)
        subject = nbn.get_nbn_status(l2altReason)
        for email in sub['subscribers']:
            message.set(get_email_message(email, subject, l2))
    
    # save updated location details
    cosmos.upsert_location(l2)

def get_email_message(email, subject, location):
    value = f"""Hi

You have signed up to receive updates for the following nbn location:
{location['addressDetail']['formattedAddress']}

{subject}

Please check the nbn website for confirmation:
https://www.nbnco.com.au/connect-home-or-business/check-your-address"""

    msg = {
        "personalizations": [ {
          "to": [{
            "email": email
            }]}],
        "subject": subject,
        "content": [{
            "type": "text/plain",
            "value": value }]}
    return json.dumps(msg)
