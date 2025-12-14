local key = "leaky_bucket_rate_limit:" .. KEYS[1]

local capacity = tonumber(ARGV[1])
local leak_rate     = tonumber(ARGV[2])
local t        = redis.call("TIME")
local now = t[1] + t[2] / 1000000

local res = redis.call("HMGET", key, "level", "last_ts")

local level  = tonumber(res[1])
local last_ts  = tonumber(res[2])

-- make sure tokens are not null
if not level then
    level = 0
    last_ts = now
end

local elapsed_time = now-last_ts

local new_level    = level - elapsed_time * leak_rate

new_level          = math.max(0, new_level)
new_level          = new_level + 1


redis.call("HMSET", key, "level", new_level, "last_ts", now)

if new_level <= capacity then
    return 1
end
return 0




