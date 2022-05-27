import azure.durable_functions as df
import logging
from datetime import timedelta


API_VERSION = 2

def orchestrator_function(context: df.DurableOrchestrationContext):
    functionName = f"'Functions.Orchestrator_v{API_VERSION}'"
    
    input = context.get_input()
    # add instance_id to dict so SendSubscriptionEmail activity has access
    input['instance_id'] = context.instance_id

    yield context.call_activity(f"SendSubscriptionEmail_v{API_VERSION}", input)

    # set up timeout task
    expiration = context.current_utc_datetime + timedelta(seconds=600)
    timeout_task = context.create_timer(expiration)

    # wait for tasks to complete
    confirmation_task = context.wait_for_external_event(
        f"ConfirmSubscriptionEvent_v{API_VERSION}")
    winner = yield context.task_any([confirmation_task, timeout_task])
    if (winner == confirmation_task):
        logging.info(
            f'{functionName} {context.instance_id} subscription confirmed')
        timeout_task.cancel()
    else:
        logging.info(
            f'{functionName} {context.instance_id} subscription timed out')

main = df.Orchestrator.create(orchestrator_function)
