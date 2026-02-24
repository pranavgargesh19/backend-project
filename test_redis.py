import redis
from app.config import Config

# Connect to Redis
r = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    password=Config.REDIS_PASSWORD,
    decode_responses=True
)

# Test setting and getting a key
r.set("test_key", "123")
print(r.get("test_key"))  # Should print 123
