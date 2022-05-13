import azure.functions as func
import json
import logging
from shared_code.nbn import get_location_from_nbn_api, get_nbn_status, upsert_location


# msg: storage queue message that triggered the function
# message: SendGrid message
def main(msg: func.QueueMessage, message: func.Out[str]) -> None:
    fn = '[LocationChecker.queueTrigger]'

    msg = msg.get_body().decode('utf-8')
    logging.info(f'{fn} Processing queue item: {msg}')
    # convert json msg string to a dict
    then = json.loads(msg)
    now = get_location_from_nbn_api(then['PartitionKey'])
    # has altReasonCode code changed?
    if now.get('altReasonCode') != then.get('altReasonCode'):
        logging.info(f"{fn} Location {now['PartitionKey']} has changed " +
            f"from {then.get('altReasonCode')} to {now.get('altReasonCode')}")
        subject = get_nbn_status(now['altReasonCode'])
        message.set(get_email_message(subject, now))
        upsert_location(now)

def get_email_message(subject, location):
    value = f"""Hi

You have signed up to receive NBN updates for the following location:
{location['formattedAddress']}

{subject}

Please check the NBN website for confirmation:
https://www.nbnco.com.au/connect-home-or-business/check-your-address"""

    msg = {
        "personalizations": [ {
          "to": [{
            "email": input['email']
            }]}],
        "subject": subject,
        "content": [{
            "type": "text/plain",
            "value": value }]}
    return json.dumps(msg)
