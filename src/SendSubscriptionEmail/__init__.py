import json
from urllib.parse import urlparse

def main(input, message):
    url = get_url(input['url'], input['instance_id'])
    value = f"""Hi

You have signed up to receive NBN updates for the following address:
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
    return True

def get_url(url: str, instance_id: str) -> str:
    parsed = urlparse(url)
    r = f'{parsed.scheme}://{parsed.netloc}/api/v1/confirm_subscription/{instance_id}'
    return r
