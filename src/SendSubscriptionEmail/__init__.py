import json
import logging
from urllib.parse import urlparse


def main(input, message):
    fn = '[SendSubscriptionEmail.activityTrigger]'
    
    logging.info(f'{fn} sending email for instance {input["instance_id"]}')
    url = get_url(input['url'], input['instance_id'])
    value = f"""Hi

You have signed up to receive NBN updates for the following location:
{input['formattedAddress']}

If this is correct please click here to confirm:
{url}"""

    msg = {
        "personalizations": [ {
          "to": [{
            "email": input['email']
            }]}],
        "subject": "Confirm your subscription",
        "content": [{
            "type": "text/plain",
            "value": value }]}

    value = json.dumps(msg)
    message.set(value)
    logging.info(f'{fn} instance {input["instance_id"]} email sent')
    return True

def get_url(url: str, instance_id: str) -> str:
    parsed = urlparse(url)
    r = f'{parsed.scheme}://{parsed.netloc}/api/v1/confirm_subscription/{instance_id}'
    return r
