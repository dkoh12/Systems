# Temporal System Demo

This folder contains a simple "Hello World" example using Temporal.

## Prerequisites

1.  **Temporal CLI**: Installed via Homebrew.
2.  **Python SDK**: `temporalio` installed in the root `.venv`.

## How to Run

### 1. Start the Temporal Server
Open a new terminal and run the development server:
```bash
temporal server start-dev
```
*This starts the Temporal Server and Web UI.*
*Web UI is available at: [http://localhost:8233](http://localhost:8233)*

### 2. Start the Worker
Open a second terminal. This process will listen for tasks and execute the code.
```bash
cd Systems/Temporal
source ../.venv/bin/activate
python worker.py
```

### 3. Run the Workflow
Open a third terminal. This script sends a request to the server to start the workflow.
```bash
cd Systems/Temporal
source ../.venv/bin/activate
python starter.py
```

## What happens?
1.  `starter.py` asks Temporal Server to run `GreetingWorkflow`.
2.  Temporal Server queues the task in `hello-world-task-queue`.
3.  `worker.py` picks up the task, executes `say_hello`, and returns the result.
4.  `starter.py` receives the result and prints it.


We've decoupled Trigger (starter.py) from Execution (worker.py)

The flow is similar to Redis pub/sub. 
We have a server running worker.py and another server running starter.py
The Temporal server is used for routing and writes everything down. 

