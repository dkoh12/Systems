Temporal is essentially a **massive, distributed State Machine**.

Under the hood, it relies on a concept called **Event Sourcing**. It doesn't store "current state" (like `status=RUNNING`); it stores a **Log of Events** that led to the current state.

Here is the step-by-step mechanics of what happens when your code runs:

### 1. The "History" (The Source of Truth)
When your workflow runs, the Temporal Server (specifically the **History Service**) writes every single step to Postgres. This is called the **Event History**.

For your "Hello David" example, the database looks roughly like this:
1.  `WorkflowExecutionStarted` (Input: "David")
2.  `ActivityTaskScheduled` (Activity: "say_hello")
3.  `ActivityTaskStarted` (Worker picked it up)
4.  `ActivityTaskCompleted` (Result: "Hello, David!")
5.  `WorkflowExecutionCompleted`

### 2. The "Replay" (The Magic Trick)
This is the part that confuses most people.

Imagine your workflow has 3 steps:
```python
val1 = await activity_A()
val2 = await activity_B()  <-- Worker crashes here!
val3 = await activity_C()
```

When the worker crashes and comes back online (or a different worker picks up the workflow), Temporal **does NOT** just jump to line 2. It doesn't know how to do that. Python doesn't support "saving RAM to disk and reloading it."

Instead, the Worker **re-runs the code from the very beginning (Line 1).**

**But wait!** Won't it run `activity_A` twice?
**No.** The Temporal SDK intercepts the call.

1.  **Worker:** Starts at Line 1. Calls `activity_A()`.
2.  **SDK:** Checks the **Event History** it got from the Server.
3.  **SDK:** "Hey, I see in the history that `activity_A` already finished with result 'Success'. I will **skip** executing the real code and just return 'Success' immediately."
4.  **Worker:** Moves to Line 2. Calls `activity_B()`.
5.  **SDK:** Checks History. "I see `activity_B` was scheduled but never finished. Okay, now I will actually execute the real code."

### 3. The "Matching Service" (The Post Office)
The Temporal Server has a **Matching Service**. It maintains in-memory queues (Task Queues).
*   It does not "push" tasks to workers.
*   Workers "poll" (long-poll) the Matching Service via gRPC, asking: "Do you have work for `hello-world-task-queue`?"
*   This allows you to run workers behind firewalls without opening ports.

### 4. The "Determinism" Rule
Because of the **Replay** mechanism described in #2, your Workflow code must be **Deterministic**.

*   **Forbidden:** `random.randint(1, 10)`
    *   *Why?* On the first run, it might be 5. On the replay (after a crash), it might be 8. The code path would diverge, and Temporal would panic.
*   **Forbidden:** `datetime.now()`
    *   *Why?* The time changes on every replay. You must use `workflow.now()`, which returns the time *recorded in the history*.

### Summary
Temporal is a system that:
1.  **Records** every step to a DB (Postgres).
2.  **Replays** your code from the start to restore state.
3.  **Skips** work that was already done by checking the history.
4.  

-------

In postgres, 
There's 2 more databases created
- Temporal (where core history data is)
- Temporal_visibility (for searching workflows. eg. "find all failed workflows")



-----


This is the most important concept in Temporal.

### 1. Activity (`say_hello`)
*   **What it is:** **The Doer**.
*   **Rules:** **Anything goes.**
    *   Can make API calls (Stripe, Twilio).
    *   Can read/write files.
    *   Can use random numbers or current time.
    *   Can be flaky (Temporal will retry it automatically).
*   **Constraint:** It has a timeout. If it takes too long, Temporal kills it.

### 2. Workflow (`GreetingWorkflow`)
*   **What it is:** **The Orchestrator**.
*   **Rules:** **Strictly Deterministic.**
    *   **NO** API calls directly.
    *   **NO** database access directly.
    *   **NO** `datetime.now()` or `random()`.
    *   **NO** threading or global variables.
*   **Job:** It just decides *which* Activity to run next.
    *   "Run Activity A."
    *   "Wait for result."
    *   "If result is 'Success', run Activity B. Else, run Activity C."

### Why the separation?
Because the **Workflow** code is replayed (re-run) every time the server recovers or a worker crashes.
*   If you put an API call `charge_credit_card()` inside the **Workflow**:
    *   Run 1: Charges card. Worker crashes.
    *   Replay 1: Charges card *again*. **Double charge!**
*   If you put it in an **Activity**:
    *   Run 1: Charges card. Temporal records "Activity Completed" in DB. Worker crashes.
    *   Replay 1: Sees "Activity Completed" in DB. **Skips** the execution. Returns the saved result. **Safe!**