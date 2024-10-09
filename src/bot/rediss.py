import redis

r = redis.Redis(
  host='expert-goshawk-28363.upstash.io',
  port=6379,
  password='AW7LAAIjcDExYjJiMzQ1Y2M0Njg0MDlmYjBlMzVlNjRhZmYzYjZmMnAxMA',
  ssl=True
)

print(r.ping())