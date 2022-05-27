import json
import logging
from urllib.parse import urlparse


API_VERSION = 2

def main(input, message) -> bool:
    functionName = f"'Functions.SendSubscriptionEmail_v{API_VERSION}'"
    instance_id = input['instance_id']
    
    logging.info(
        f'{functionName} Sending email for instance {instance_id}')
    url = get_url(input['url'], instance_id)
    value = f"""Hi

You have signed up to receive nbn updates for the following location:
{input['formattedAddress']}

If this is correct, please click this link within 10 minutes to confirm:
{url}
"""

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
    logging.info(f'{functionName} Subscription email sent for durable ' +
                 f'instance {instance_id}')
    return True

def get_url(url: str, instance_id: str) -> str:
    parsed = urlparse(url)
    return (f'{parsed.scheme}://{parsed.netloc}/api/v{API_VERSION}' +
            f'/confirm_subscription/{instance_id}')
