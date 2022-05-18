import azure.functions as func
import json
import logging
from shared_code.nbn import get_location_from_nbn_api, get_nbn_status, upsert_location


API_VERSION = 2

# msg: storage queue message that triggered the function
# message: SendGrid message
def main(msg: func.QueueMessage, message: func.Out[str]) -> None:
    functionName = f"'Functions.LocationChecker_v{API_VERSION}'"

    msg = msg.get_body().decode('utf-8')
    logging.info(f'{functionName} Processing queue item: {msg}')
    # convert json msg string to a dict
    then = json.loads(msg)
    now = get_location_from_nbn_api(then['PartitionKey'])
    # has altReasonCode code changed?
    if now.get('altReasonCode') != then.get('altReasonCode'):
        logging.info(f'{functionName} Location {now["PartitionKey"]} has ' +
                     f'changed from {then.get("altReasonCode")} to ' +
                     f'{now.get("altReasonCode")}')
        subject = get_nbn_status(now['altReasonCode'])
        for email in then['subscribers']:
            message.set(get_email_message(email, subject, now))
        upsert_location(now)

def get_email_message(email, subject, location):
    value = f"""Hi

You have signed up to receive NBN updates for the following location:
{location['formattedAddress']}

{subject}

Please check the NBN website for confirmation:
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
