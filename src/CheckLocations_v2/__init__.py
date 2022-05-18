from webbrowser import get
import azure.functions as func
import json
import logging
import typing
from shared_code.table import AzureTableClient
from shared_code.cosmos import get_all_locations, get_location_subscribers


API_VERSION = 2

# check all locations in table
# if they have a subscriber add them to the queue
def main(mytimer: func.TimerRequest, msg: func.Out[typing.List[str]]) -> None:
    functionName = f"'Functions.CheckLocations_v{API_VERSION}'"

    if mytimer.past_due:
        logging.info(f'{functionName} The timer is past due!')
    
    count = 0
    messages = []
    for location in get_all_locations():
        count += 1
        for subscriber in get_location_subscribers(location['id']):
            if not location.get('subscribers'):
                location['subscribers'] = []
            location['subscribers'].append(subscriber['RowKey'])
        # add this location to the queue if it has subscribers
        if location.get('subscribers'):
            messages.append(json.dumps(location))
    
    logging.info(f'{functionName} Checked {count} locations for subscribers')
    if messages:
        msg.set(messages)
        logging.info(f'{functionName} Added {len(messages)} message(s) to the queue')
    else:
        logging.info(f'{functionName} No messages add to the queue')
