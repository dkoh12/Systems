This is the most fascinating part of Temporal. To understand it, you have to stop thinking about "running code" and start thinking about **"generating a save file."**

Here is the deep dive into the **Data Flow** and **Fault Tolerance**.

### The Core Concept: The "Workflow Task" Loop
Temporal breaks your code execution into small chunks called **Workflow Tasks**.
*   **Worker:** "I ran the code until I hit an `await`. Here is what I want to do next."
*   **Server:** "Okay, I wrote that down. Go to sleep. I'll wake you up when that thing is done."

---

### Scenario 1: The Happy Path (Data Flow)
Let's trace your `GreetingWorkflow` step-by-step.

**1. The Start**
*   **Starter.py:** Sends `StartWorkflow` request.
*   **Server:** Writes Event #1 to Postgres: `WorkflowExecutionStarted`.
*   **Server:** Puts a **Workflow Task** into the `hello-world-task-queue`.

**2. The Decision (Workflow Worker)**
*   **Worker:** Polls the queue, gets the task.
*   **Worker (SDK):** Starts running `GreetingWorkflow.run()`.
*   **Code:** Hits `await workflow.execute_activity(say_hello, ...)`.
*   **Worker (SDK):** Pauses execution. It realizes it cannot proceed without the activity result.
*   **Worker:** Sends a **Command** to Server: "Schedule Activity `say_hello`".
*   **Server:** Writes Event #2: `WorkflowTaskCompleted`.
*   **Server:** Writes Event #3: `ActivityTaskScheduled`.
*   **Server:** Puts an **Activity Task** into the queue.

**3. The Action (Activity Worker)**
*   **Worker:** Polls queue, gets the Activity Task.
*   **Worker:** Executes `say_hello("David")`. It returns "Hello, David!".
*   **Worker:** Sends result to Server.
*   **Server:** Writes Event #4: `ActivityTaskStarted`.
*   **Server:** Writes Event #5: `ActivityTaskCompleted` (Result: "Hello, David!").
*   **Server:** Creates a new **Workflow Task** to wake up the workflow.

**4. The Completion**
*   **Worker:** Polls queue, gets the Workflow Task.
*   **Worker (SDK):** **REPLAYS** the code from line 1.
    *   *Line 1 (Call Activity):* SDK checks history. Sees Event #5 (`ActivityTaskCompleted`). It **skips** scheduling the activity and just injects "Hello, David!" as the result.
*   **Code:** Returns "Hello, David!".
*   **Worker:** Sends "Complete Workflow" command.
*   **Server:** Writes Event #6: `WorkflowExecutionCompleted`.

---

### Scenario 2: The Worker Crash (Fault Tolerance)
What if the Worker crashes **while running the Activity**?

1.  **Server:** Gives Activity Task to Worker A.
2.  **Server:** Starts a "Start-To-Close" timer (e.g., 5 seconds).
3.  **Worker A:** Pulls the plug / crashes / burns.
4.  **Server:** 5 seconds pass. No response.
5.  **Server:** **Times out** the attempt.
6.  **Server:** Writes `ActivityTaskTimedOut` (or `Retrying`) to history.
7.  **Server:** Puts the Activity Task **back into the queue**.
8.  **Worker B:** Picks up the task and runs it.

**Result:** The system self-heals. You don't write retry logic; the infrastructure handles it.

---

### Scenario 3: The "Replay" (Event Sourcing)
This is the "Magic Trick." What if the Worker crashes **in the middle of the Workflow logic**?

Imagine this code:
```python
# Step 1
val1 = await activity_A() 
# Step 2
print("I am here") 
# Step 3
val2 = await activity_B() 
```

**The Crash:**
1.  Worker runs `activity_A`. Server records result.
2.  Worker is about to run `activity_B`. **CRASH.**

**The Recovery (New Worker comes online):**
1.  Server hands the Workflow Task to the New Worker.
2.  Server sends the **Full Event History** (Events 1-5) to the New Worker.
3.  **New Worker:** Starts at Line 1.
    *   `await activity_A()`
    *   **SDK Intercept:** "Hold on. I see in History that `activity_A` finished. I will NOT run it. I will just return the value `42` that is stored in the history."
4.  **New Worker:** Reaches Line 2. Prints "I am here".
5.  **New Worker:** Reaches Line 3. `await activity_B()`.
    *   **SDK Intercept:** "I check History. `activity_B` is NOT in the history. Okay, Server, please schedule `activity_B`."

**Result:** The workflow resumes exactly where it left off, but it did so by **fast-forwarding** through the past.

---

### Scenario 4: The Long Sleep (Durability)
What if you have `await asyncio.sleep(30 days)`?

1.  **Worker:** Hits the sleep line.
2.  **Worker:** Sends "Add Timer (30 days)" command to Server.
3.  **Worker:** **Dies.** (It finishes the task and clears its memory. It does NOT block a thread for 30 days).
4.  **Server:** Stores the timer in Postgres.
5.  **30 Days Later:**
    *   Server clock hits the time.
    *   Server creates a new Workflow Task.
    *   Worker picks it up.
    *   Worker **Replays** the entire history from 30 days ago up to the sleep statement.
    *   SDK sees "Timer Fired" event in history.
    *   Worker moves to the next line of code.

**Result:** You can have millions of "sleeping" workflows consuming **Zero CPU and Zero RAM** on your workers. They only exist as rows in Postgres.