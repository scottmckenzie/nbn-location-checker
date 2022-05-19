import logging
from shared_code.cosmos import upsert_location


API_VERSION = 2

def main(location: dict) -> bool:
    functionName = f"'Functions.InsertLoction_v{API_VERSION}'"
    logging.info(
        f'{functionName} activityTrigger inserting: {location["id"]}')
    upsert_location(location)
    return True
