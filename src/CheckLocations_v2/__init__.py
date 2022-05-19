import azure.functions as func
import json
import logging
import typing
import shared_code.cosmos as cosmos


API_VERSION = 2

# check all locations in table
# if they have a subscriber add them to the queue
def main(mytimer: func.TimerRequest, msg: func.Out[typing.List[str]]) -> None:
    functionName = f"'Functions.CheckLocations_v{API_VERSION}'"

    if mytimer.past_due:
        logging.info(f'{functionName} The timer is past due!')
    
    count = 0
    messages = []
    for location in cosmos.get_all_locations():
        # ignore technologies not eligible for upgrade
        if location['addressDetail']['techType'] not in ['FTTC','FTTN']:
            continue
        count += 1
        for subscriber in cosmos.get_location_subscribers(location['id']):
            if not location.get('subscribers'):
                location['subscribers'] = []
            location['subscribers'].append(subscriber['email'])
        # add this location to the queue if it has subscribers
        if location.get('subscribers'):
            messages.append(json.dumps(location))
    
    logging.info(f'{functionName} Checked {count} locations for subscribers')
    if messages:
        msg.set(messages)
        logging.info(f'{functionName} Added {len(messages)} message(s) to the queue')
    else:
        logging.info(f'{functionName} No messages add to the queue')
