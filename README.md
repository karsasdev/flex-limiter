# Flex-Limiter

A configurable rate-limiting engine with pluggable algorithms (token bucket, leaky bucket, sliding window).

#### **Start Redis**:
   ```bash
   docker-compose up -d limiterstore
   ```

## Rate Limiting Formulas

### Token Bucket
Gives some flexibility by allowing bursts when idle, while still limiting how fast requests can go on average.
```text
tokens = min(capacity, tokens + (now - last_ts) * refill_rate)
allow request if tokens >= 1, then tokens -= 1
```

### Leaky Bucket
Keeps traffic smooth and predictable by allowing requests at a steady speed and pushing back on bursts.
```text
level = max(0, level - (now - last_ts) * leak_rate) + 1
allow request if level <= capacity
```

### Sliding window counter(2-bucket approximation)
Limits requests by looking at how many came in over the last few seconds, so traffic is smoothed out instead of resetting suddenly at fixed time boundaries.
```text
window_start = now - window_size
curr_bucket_index = floor(now / bucket_size)
effective_request_count = curr_bucket_count + (overlap / bucket_size) * prev_bucket_count
allow request if effective_request_count < requests_allowed
```


### Test Scenarios

- **Normal requests**: 5 requests within limit
- **Burst test**: 10 rapid requests (5 succeed, 5 blocked)
- **Time-based recovery**: Exhaust limit, wait, then request succeeds
- **User isolation**: Limits applied independently per user

### Test Outcome

| Behavior       | Leaky Bucket              | Token Bucket            | Sliding Window Counter            |
| -------------- | ------------------------- | ----------------------- | --------------------------------- |
| Burst handling | Blocks immediately        | Allows short bursts     | Smoothly limits bursts            |
| After waiting  | Few requests allowed      | Many requests allowed   | Requests allowed gradually        |
| Traffic shape  | Steady, flat              | Spiky after idle        | Smooth, time-distributed          |
| Best use       | Protect backend systems   | User-facing APIs        | Accurate API rate limiting        |

