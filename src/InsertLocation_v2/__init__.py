import logging
from shared_code.cosmos import upsert_location

def main(location: dict) -> bool:
    functionName = "'Functions.InsertLoction'"
    logging.info(
        f'{functionName} activityTrigger inserting: {location["id"]}')
    upsert_location(location)
    return True
