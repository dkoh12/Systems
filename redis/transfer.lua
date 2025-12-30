-- This script is executed within the Redis server.
-- The 'redis' global object is provided by the Redis Lua environment.
-- KEYS and ARGV are global arrays containing keys and arguments passed to the script.

local sender = KEYS[1]
local receiver = KEYS[2]
local amount = tonumber(ARGV[1])

-- Get current balance of sender
local sender_balance = tonumber(redis.call('GET', sender) or 0)

-- Check if sender has enough funds
if sender_balance >= amount then
    -- Perform the transfer atomically
    redis.call('DECRBY', sender, amount)
    redis.call('INCRBY', receiver, amount)
    return {1, sender_balance - amount} -- Return success and new balance
else
    return {0, sender_balance} -- Return failure and current balance
end
