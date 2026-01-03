import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

# Import the workflow and activity we defined
from workflow import GreetingWorkflow, say_hello, get_weather, send_email

async def main():
    # 1. Connect to the Temporal Server
    # By default, 'temporal server start-dev' runs on localhost:7233
    client = await Client.connect("localhost:7233")

    # 2. Create a Worker
    # The worker listens to a specific "Task Queue"
    worker = Worker(
        client,
        task_queue="hello-world-task-queue",
        workflows=[GreetingWorkflow],
        activities=[say_hello, get_weather, send_email],
    )

    print("Worker started. Listening for tasks...")
    # 3. Run the worker (blocks indefinitely)
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
