import azure.functions as func
import json
import logging
import shared_code.cosmos_aio as cosmos
from shared_code import nbn


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
    # left is our altReasonCode, right is nbn's
    left = await cosmos.get_alt_reason_code(sub['csa_id'], location_id)

    location = await nbn.get_location_async(location_id)
    if location is None:
        raise Exception(f'Failed to get nbn location {location_id}')
    if location['addressDetail']['techType'] == 'FTTP':
        #TODO send email advising of upgrade and sub removal
        # delete subscription
        await cosmos.delete_subscription(sub)
        await cosmos.upsert_location(location)
        return

    right = location['addressDetail']['altReasonCode']
    # has altReasonCode code changed?
    if left == right:
        return
    logging.info(f'{functionName} Location {location_id} has changed from '
        f'{left} to {right}')

    # construct email message(s)
    subject = nbn.get_nbn_status(right)
    for email in sub['subscribers']:
        message.set(get_email_message(email, subject, location))

    # save updated location details
    await cosmos.upsert_location(location)

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
