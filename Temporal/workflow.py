from datetime import timedelta
from temporalio import activity, workflow

# --- 1. Define the Activities ---

@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@activity.defn
async def get_weather(city: str) -> str:
    # Simulate an API call
    return f"Sunny in {city}"

@activity.defn
async def send_email(email: str, message: str) -> str:
    # Simulate sending an email
    return f"Email sent to {email}: {message}"

# --- 2. Define the Workflow ---

@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        # Step 1: Say Hello
        greeting = await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=5),
        )
        
        # Step 2: Get Weather (Simulated dependency)
        # We can use the result of the previous step or new data
        weather = await workflow.execute_activity(
            get_weather,
            "San Francisco",
            start_to_close_timeout=timedelta(seconds=5),
        )
        
        # Step 3: Send Email (Simulated side effect)
        final_message = f"{greeting} It is {weather}."
        email_result = await workflow.execute_activity(
            send_email,
            args=["user@example.com", final_message], # Note: args must be a list/tuple if multiple
            start_to_close_timeout=timedelta(seconds=5),
        )
        
        return f"Workflow Complete! Result: {email_result}"
