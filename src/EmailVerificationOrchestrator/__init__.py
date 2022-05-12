import azure.durable_functions as df
import azure.functions as func
import logging
from datetime import timedelta


def orchestrator_function(context: df.DurableOrchestrationContext):
    input = context.get_input()
    # add instance_id to input dict so SendSubscriptionEmail activity has access to it
    input['instance_id'] = context.instance_id

    # call SendSubscriptionEmail activity
    yield context.call_activity("SendSubscriptionEmail", input)

    # set up timeout task
    expiration = context.current_utc_datetime + timedelta(seconds=600)
    timeout_task = context.create_timer(expiration)

    # wait for tasks to complete
    confirmation_task = context.wait_for_external_event("ConfirmSubscriptionEvent")
    winner = yield context.task_any([confirmation_task, timeout_task])
    if (winner == confirmation_task):
        logging.info('subscription confirmed')
    if not timeout_task.is_completed:
        # All pending timers must be complete or canceled before the function exits.
        timeout_task.cancel()

main = df.Orchestrator.create(orchestrator_function)
