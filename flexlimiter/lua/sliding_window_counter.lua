local key = "sliding_window_counter_rate_limit:" .. KEYS[1]

local window_size = tonumber(ARGV[1])
local bucket_size = tonumber(ARGV[2])
local requests_allowed = tonumber(ARGV[3])

local t        = redis.call("TIME")
local now      = t[1] + t[2] / 1000000

local window_start = now - window_size

local curr_bucket_index = math.floor(now / bucket_size)
local prev_bucket_index = curr_bucket_index - 1

local curr_bucket_key = key .. ":" .. curr_bucket_index
local prev_bucket_key = key .. ":" .. prev_bucket_index

local prev_bucket_end = (prev_bucket_index + 1) * bucket_size
local overlap           = prev_bucket_end - window_start

local curr_count = tonumber(redis.call("GET", curr_bucket_key)) or 0
local prev_count        = tonumber(redis.call("GET", prev_bucket_key)) or 0


local weight = overlap / bucket_size

local current_requests_count = (weight * prev_count) + curr_count

if current_requests_count >= requests_allowed then
    return 0
end
redis.call("INCR", curr_bucket_key)
redis.call("EXPIRE", curr_bucket_key, window_size * 2)
return 1

