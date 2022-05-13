import azure.functions as func
import json
import logging
import typing
from shared_code.table import AzureTableClient


# check all locations in table
# if they have a subscriber add them to the queue
def main(mytimer: func.TimerRequest, msg: func.Out[typing.List[str]]) -> None:
    fn = '[CheckLocations.timerTrigger]'

    if mytimer.past_due:
        logging.info(f'{fn} The timer is past due!')
    
    count = 0
    messages = []
    filter = f"RowKey eq '.'"
    with AzureTableClient.get() as table:
        # iterate over all locations
        for location in table.query_entities(filter):
            count += 1
            partition_key = location['PartitionKey']
            filter = f"PartitionKey eq '{partition_key}' and RowKey ne '.'"
            # iterate over all subscribers to this location
            for subscriber in table.query_entities(filter):
                if not location.get('subscribers'):
                    location['subscribers'] = []
                location['subscribers'].append(subscriber['RowKey'])
            # add this location to the queue if it has subscribers
            if location.get('subscribers'):
                messages.append(json.dumps(location))
    
    logging.info(f'{fn} Checked {count} locations for subscribers')
    if messages:
        msg.set(messages)
        logging.info(f'{fn} Added {len(messages)} message(s) to the queue')
    else:
        logging.info(f'{fn} No messages add to the queue')
