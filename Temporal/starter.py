import asyncio
import sys
from temporalio.client import Client

# Import the workflow definition (so we can use it in the execute_workflow call)
from workflow import GreetingWorkflow

async def main():
    # 1. Connect to the Temporal Server
    client = await Client.connect("localhost:7233")

    # 2. Start the Workflow
    # We send a signal to the server to start 'GreetingWorkflow'
    # The server puts a task on the 'hello-world-task-queue'
    print("Starting workflow...")
    result = await client.execute_workflow(
        GreetingWorkflow.run,
        "David",  # The argument to the workflow
        id="hello-workflow-id",
        task_queue="hello-world-task-queue",
    )

    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
