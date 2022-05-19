import azure.functions as func
import json
import logging
from shared_code import cosmos, nbn


API_VERSION = 2

# msg: storage queue message that triggered the function
# message: SendGrid message
def main(msg: func.QueueMessage, message: func.Out[str]) -> None:
    functionName = f"'Functions.LocationChecker_v{API_VERSION}'"

    msg = msg.get_body().decode('utf-8')
    logging.info(f'{functionName} Processing queue item: {msg}')
    
    # convert json msg string to a dict
    l1 = json.loads(msg)
    l1altReason = l1['addressDetail']['altReasonCode']
    location_id = l1['id']

    l2 = nbn.get_location(location_id)
    l2altReason = l2['addressDetail']['altReasonCode']
    
    # has altReasonCode code changed?
    if l1altReason == l2altReason:
        return
    logging.info(f'{functionName} Location {location_id} has changed from '
        f'{l1altReason} to {l2altReason}')
    
    # construct email message(s)
    subject = nbn.get_nbn_status(l2altReason)
    for email in l1['subscribers']:
        message.set(get_email_message(email, subject, l2))
    
    # save new location details
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
