import azure.functions as func
import json
import logging
import typing
import shared_code.cosmos as cosmos


API_VERSION = 2

def main(mytimer: func.TimerRequest, msg: func.Out[typing.List[str]]) -> None:
    functionName = f"'Functions.ProcessSubscriptions_v2{API_VERSION}'"
    
    if mytimer.past_due:
        logging.info(f'{functionName} The timer is past due!')
    
    messages = []
    for sub in cosmos.get_subscriptions():
        messages.append(json.dumps(sub))
    
    if messages:
        msg.set(messages)
        logging.info(f'{functionName} Added {len(messages)} message(s) to the queue')
        return
    
    logging.info(f'{functionName} No messages add to the queue')
