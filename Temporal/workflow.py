from datetime import timedelta
from temporalio import activity, workflow

# --- 1. Define the Activity ---
# Activities are where the actual work happens (API calls, DB writes, etc.)
@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello, {name}!"

# --- 2. Define the Workflow ---
# Workflows orchestrate activities. They must be deterministic.
@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        # Call the activity
        # We set a timeout so Temporal knows when to give up if the worker is down
        result = await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=5),
        )
        return result
