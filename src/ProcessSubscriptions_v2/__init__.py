import azure.functions as func
import json
import logging
import os
import time
import shared_code.cosmos as cosmos
from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy


API_VERSION = 2

def main(mytimer: func.TimerRequest) -> None:
    functionName = f"'Functions.ProcessSubscriptions_v{API_VERSION}'"
    
    if mytimer.past_due:
        logging.info(f'{functionName} The timer is past due!')
    
    conn_str = os.getenv('AzureWebJobsStorage')
    queue_name = os.getenv('ProcessSubscriptions_v2.QueueName')
    queue_client = QueueClient.from_connection_string(
        conn_str, queue_name,
        message_encode_policy = BinaryBase64EncodePolicy())

    message_count = 0
    for sub in cosmos.get_subscriptions():
        message = json.dumps(sub)
        queue_client.send_message(message.encode('ascii'))
        message_count += 1
        time.sleep(0.5)
    
    if message_count > 0:
        logging.info(
            f'{functionName} Added {message_count} message(s) to the queue')
        return
    
    logging.info(f'{functionName} No messages add to the queue')
