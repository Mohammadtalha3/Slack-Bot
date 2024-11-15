# import redis

# r = redis.Redis(
#   host='expert-goshawk-28363.upstash.io',
#   port=6379,
#   password='AW5SAAIjcDFkMjQwYmFkOTA5Y2U0ZDljOTQ2NjU3ZjAxODdlNGRkN3AxMA',
#   ssl=True
# )

# # print(r.ping())

# r.set('foo', 'bar')
# print(r.get('foo'))

# from upstash_redis import Redis

# redis = Redis(url="https://happy-griffon-28242.upstash.io", token="AW5SAAIjcDFkMjQwYmFkOTA5Y2U0ZDljOTQ2NjU3ZjAxODdlNGRkN3AxMA")

# redis.set("foo", "bar")
# value = redis.get("foo")

# print(value)

import redis

r = redis.Redis(
  host='happy-griffon-28242.upstash.io',
  port=6379,
  password='AW5SAAIjcDFkMjQwYmFkOTA5Y2U0ZDljOTQ2NjU3ZjAxODdlNGRkN3AxMA',
  ssl=True
)

r.set('foo', 'bar')
print(r.get('foo'))