import redis
import time

"""
Redis Streams + Consumer Groups Demo
Stream: order_events

https://devopedia.org/redis-streams

Key idea:
- A consumer GROUP lets multiple consumers share the work of processing a stream.
- Each message is delivered to only ONE consumer in the group (like a task queue).
- Messages stay "pending" until the consumer ACKs them.
- If a consumer crashes before ACKing, another consumer can CLAIM the message.

Compare to plain XREAD (no group):
- Every reader gets EVERY message independently (fan-out / broadcast).
- Consumer groups give you competing consumers (load-balanced).
"""

STREAM_KEY = "order_events"
GROUP_NAME = "order_processors"


def setup(r: redis.Redis):
    # Clean slate
    r.delete(STREAM_KEY)
    print(f"Deleted existing '{STREAM_KEY}' stream.\n")

    # Add some orders to the stream before any consumer is ready.
    # This shows that streams PERSIST messages — consumers catch up later.
    orders = [
        {"order_id": "ORD-001", "item": "laptop", "qty": "1", "status": "new"},
        {"order_id": "ORD-002", "item": "mouse",  "qty": "2", "status": "new"},
        {"order_id": "ORD-003", "item": "monitor","qty": "1", "status": "new"},
        {"order_id": "ORD-004", "item": "keyboard","qty": "3","status": "new"},
        {"order_id": "ORD-005", "item": "webcam", "qty": "1", "status": "new"},
    ]
    print("--- Producing 5 orders onto the stream ---")
    for order in orders:
        msg_id = r.xadd(STREAM_KEY, order)
        print(f"  XADD {STREAM_KEY} * -> {msg_id.decode()} | {order['order_id']} ({order['item']})")

    print(f"\nStream length: {r.xlen(STREAM_KEY)} messages\n")

    # Create the consumer group, reading from the very beginning ('0')
    # Use mkstream=True so it auto-creates the stream if needed
    try:
        r.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
        print(f"Created consumer group '{GROUP_NAME}' starting from ID 0 (read all history)\n")
    except redis.exceptions.ResponseError as e:
        # Group already exists — reset it
        print(f"Group already exists, resetting: {e}")
        r.xgroup_setid(STREAM_KEY, GROUP_NAME, "0")
        print(f"Reset '{GROUP_NAME}' to start from beginning.\n")


def consumer_read(r: redis.Redis, consumer_name: str, count: int = 2):
    """
    XREADGROUP: Read up to `count` undelivered messages as `consumer_name`.
    '>' means "give me messages not yet delivered to any consumer in this group".
    """
    print(f"[{consumer_name}] Reading up to {count} message(s)...")
    results = r.xreadgroup(
        groupname=GROUP_NAME,
        consumername=consumer_name,
        streams={STREAM_KEY: ">"},   # '>' = only new/undelivered messages
        count=count,
        block=0                       # 0 = non-blocking
    )

    if not results:
        print(f"[{consumer_name}] No new messages.\n")
        return []

    received = []
    for stream, messages in results:
        for msg_id, data in messages:
            decoded = {k.decode(): v.decode() for k, v in data.items()}
            print(f"  [{consumer_name}] Got {msg_id.decode()} -> {decoded}")
            received.append(msg_id)

    print()
    return received


def ack_messages(r: redis.Redis, consumer_name: str, msg_ids: list):
    """
    XACK: Tell the group this consumer successfully processed the message.
    It moves out of the Pending Entries List (PEL).
    """
    if not msg_ids:
        return
    r.xack(STREAM_KEY, GROUP_NAME, *msg_ids)
    acked = [mid.decode() for mid in msg_ids]
    print(f"[{consumer_name}] ACKed: {acked}\n")


def show_pending(r: redis.Redis):
    """
    XPENDING: Show messages delivered but not yet ACKed.
    These are 'in-flight' — consumer received them but hasn't confirmed processing.
    """
    # Summary: total pending + per-consumer breakdown
    summary = r.xpending(STREAM_KEY, GROUP_NAME)
    print(f"--- Pending summary for group '{GROUP_NAME}' ---")
    print(f"  Total pending: {summary['pending']}")
    if summary['pending'] > 0:
        print(f"  ID range: {summary['min']} .. {summary['max']}")
        print(f"  Per consumer: {summary['consumers']}")

    # Detailed list: each pending message with idle time + delivery count
    details = r.xpending_range(STREAM_KEY, GROUP_NAME, min="-", max="+", count=10)
    if details:
        print("  Details:")
        for entry in details:
            print(f"    ID={entry['message_id'].decode()} "
                  f"consumer={entry['consumer'].decode()} "
                  f"delivered={entry['times_delivered']}x "
                  f"idle={entry['time_since_delivered']}ms")
    print()


def simulate_crash_and_reclaim(r: redis.Redis):
    """
    Simulate: worker-2 crashes without ACKing. worker-1 reclaims its messages.

    XCLAIM transfers ownership of a pending message to a new consumer.
    In production you'd check idle time > some threshold (e.g. 30s).
    """
    print("--- Simulating crash: worker-2 never ACKed its messages ---")
    print("--- worker-1 will reclaim them via XCLAIM ---\n")

    # Find pending messages owned by worker-2
    details = r.xpending_range(STREAM_KEY, GROUP_NAME, min="-", max="+", count=10)
    worker2_ids = [
        e["message_id"] for e in details
        if e["consumer"].decode() == "worker-2"
    ]

    if not worker2_ids:
        print("No pending messages from worker-2 to reclaim.\n")
        return

    # XCLAIM with min_idle_time=0 (in ms) so we don't have to wait
    claimed = r.xclaim(STREAM_KEY, GROUP_NAME, "worker-1", min_idle_time=0, message_ids=worker2_ids)
    print(f"[worker-1] Reclaimed {len(claimed)} message(s) from worker-2:")
    for msg_id, data in claimed:
        decoded = {k.decode(): v.decode() for k, v in data.items()}
        print(f"  {msg_id.decode()} -> {decoded}")
    print()

    # Now ACK them as worker-1
    ack_messages(r, "worker-1", [msg_id for msg_id, _ in claimed])


def main():
    r = redis.Redis(host="localhost", port=6379, db=0)
    try:
        r.ping()
    except redis.ConnectionError:
        print("Error: Could not connect to Redis.")
        return

    # ── 1. Setup: produce messages & create group ────────────────────────────
    setup(r)

    # ── 2. Two consumers competing for messages ──────────────────────────────
    print("=== Step 1: Two workers read from the SAME group (load-balanced) ===\n")
    # worker-1 takes 2 messages, worker-2 takes 2, worker-1 takes 1 more
    ids_w1_batch1 = consumer_read(r, "worker-1", count=2)
    ids_w2_batch1 = consumer_read(r, "worker-2", count=2)
    ids_w1_batch2 = consumer_read(r, "worker-1", count=2)  # gets the last 1

    # ── 3. Show pending (nothing ACKed yet) ──────────────────────────────────
    print("=== Step 2: All 5 messages are pending (none ACKed yet) ===\n")
    show_pending(r)

    # ── 4. worker-1 ACKs its messages; worker-2 "crashes" ───────────────────
    print("=== Step 3: worker-1 ACKs its messages. worker-2 does NOT (simulating crash). ===\n")
    ack_messages(r, "worker-1", ids_w1_batch1 + ids_w1_batch2)
    show_pending(r)

    # ── 5. Reclaim worker-2's unACKed messages ───────────────────────────────
    print("=== Step 4: worker-1 reclaims and re-processes worker-2's pending messages ===\n")
    simulate_crash_and_reclaim(r)

    # ── 6. Final state ───────────────────────────────────────────────────────
    print("=== Step 5: Final pending check (should be 0) ===\n")
    show_pending(r)

    print("Done! All messages processed and acknowledged.")
    print("\nUseful redis-cli commands to inspect manually:")
    print(f"  XRANGE {STREAM_KEY} - +")
    print(f"  XPENDING {STREAM_KEY} {GROUP_NAME} - + 10")
    print(f"  XINFO GROUPS {STREAM_KEY}")
    print(f"  XINFO CONSUMERS {STREAM_KEY} {GROUP_NAME}")


if __name__ == "__main__":
    main()
