local key = "token_bucket_rate_limit:" .. KEYS[1]

local capacity = tonumber(ARGV[1])
local rate     = tonumber(ARGV[2])
local t        = redis.call("TIME")
local now = t[1] + t[2] / 1000000

local res = redis.call("HMGET", key, "tokens", "last_ts")

local tokens  = tonumber(res[1])
local last_ts  = tonumber(res[2])

-- make sure tokens are not null
if not tokens then
    tokens = capacity
    last_ts = now
end

local elapsed_time = now-last_ts

tokens             = tokens + elapsed_time * rate

tokens             = math.min(capacity, tokens)

if tokens < 1 then
    redis.call("HMSET", key, "tokens", tokens, "last_ts", now)
    return 0
end

tokens = tokens - 1
redis.call("HMSET", key, "tokens", tokens, "last_ts", now)
return 1




