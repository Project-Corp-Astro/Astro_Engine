# 🔧 Redis Configuration Documentation

## Overview
This document provides comprehensive configuration details for the Redis caching implementation in Astro Engine.

## Redis Setup

### Installation
```bash
# macOS (via Homebrew)
brew install redis

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# Windows (via chocolatey)
choco install redis-64
```

### Starting Redis
```bash
# Start Redis server
redis-server

# Start Redis with custom config
redis-server /path/to/redis.conf

# Check if Redis is running
redis-cli ping
# Should return: PONG
```

## Environment Configuration

### Required Environment Variables
```bash
# Redis connection settings
REDIS_HOST=localhost          # Redis server host
REDIS_PORT=6379              # Redis server port  
REDIS_DB=0                   # Redis database number
REDIS_PASSWORD=              # Redis password (if auth enabled)
REDIS_TIMEOUT=5.0            # Connection timeout in seconds
REDIS_CONNECT_TIMEOUT=5.0    # Connection establishment timeout

# Cache settings
CACHE_DEFAULT_TTL=86400      # Default cache TTL (24 hours)
CACHE_PREFIX=astro_engine:   # Cache key prefix

# Application settings
REDIS_URL=redis://localhost:6379/0  # Full Redis URL (alternative)
```

### Example .env File
```bash
# .env file for development
FLASK_ENV=development
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_DEFAULT_TTL=86400
LOG_LEVEL=INFO
```

## Cache Configuration

### Cache Key Structure
```
astro_engine:{hash}
```

Where `{hash}` is an MD5 hash of:
- birth_date
- birth_time 
- latitude (rounded to 6 decimals)
- longitude (rounded to 6 decimals)
- timezone_offset
- ayanamsa
- calculation_type

### Cache TTL Settings
```python
CACHE_TTLS = {
    'natal_chart': 86400,        # 24 hours - stable calculation
    'navamsa_chart': 86400,      # 24 hours - stable calculation
    'd3_chart': 86400,           # 24 hours - stable calculation
    'transit_chart': 3600,       # 1 hour - dynamic data
    'dashas': 86400,             # 24 hours - stable calculation
    'composite': 86400,          # 24 hours - stable calculation
    'synastry': 86400,           # 24 hours - stable calculation
}
```

## Performance Optimization

### Redis Configuration (redis.conf)
```bash
# Memory optimization
maxmemory 256mb
maxmemory-policy allkeys-lru

# Performance settings
tcp-keepalive 300
timeout 0

# Persistence (for production)
save 900 1
save 300 10
save 60 10000

# For development (disable persistence)
# save ""
```

### Connection Pool Settings
```python
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': False,
    'socket_timeout': 5.0,
    'socket_connect_timeout': 5.0,
    'retry_on_timeout': True,
    'health_check_interval': 30,
    'max_connections': 20
}
```

## Monitoring and Management

### Cache Statistics Endpoint
```http
GET /cache/stats

Response:
{
    "hit_rate": 85.5,
    "total_operations": 1247,
    "cache_hits": 1066,
    "cache_misses": 181,
    "cache_errors": 0,
    "redis_available": true,
    "memory_cache_size": 0,
    "default_ttl": 86400,
    "redis_memory_usage": "12.5M",
    "redis_keys": 156
}
```

### Cache Management Endpoints
```http
# Clear all cache
DELETE /cache/clear

# Clear cache by pattern
DELETE /cache/clear/{pattern}

# Examples:
DELETE /cache/clear/natal_chart
DELETE /cache/clear/d3_chart
```

### Redis CLI Commands
```bash
# Connect to Redis
redis-cli

# View all keys
KEYS astro_engine:*

# Get cache statistics
INFO memory
INFO stats

# Check specific key
GET astro_engine:abc123def456

# Delete keys by pattern
EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 astro_engine:*

# Monitor cache activity
MONITOR
```

## Error Handling

### Fallback Behavior
When Redis is unavailable:
1. Cache manager falls back to in-memory cache
2. Limited to 1000 items (LRU eviction)
3. No persistence across application restarts
4. Performance degrades gracefully

### Error Logging
```python
# Cache errors are logged with context
logger.error(f"Redis connection failed: {error}")
logger.warning(f"Falling back to memory cache")
```

## Security Configuration

### Redis Security (Production)
```bash
# redis.conf security settings
bind 127.0.0.1              # Bind to specific IP
protected-mode yes          # Enable protected mode
requirepass your_password   # Set password

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
```

### Application Security
```python
# Environment variables for sensitive data
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_SSL_CERT = os.getenv('REDIS_SSL_CERT')
REDIS_SSL_KEY = os.getenv('REDIS_SSL_KEY')
```

## Production Deployment

### Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf

  astro_engine:
    build: .
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis

volumes:
  redis_data:
```

### Kubernetes Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Testing and Validation

### Performance Benchmarks
```bash
# Redis performance test
redis-benchmark -h localhost -p 6379 -n 1000 -c 10

# Application cache test
python3 test_redis_connection.py
python3 validate_cache_implementation.py
python3 phase1_integration_test.py
```

### Expected Performance
- SET operations: 2000+ ops/sec
- GET operations: 4000+ ops/sec  
- Cache hit rate: >70% in production
- Response time improvement: 5-20x faster

## Troubleshooting

### Common Issues
1. **Connection Refused**
   ```bash
   # Check if Redis is running
   redis-cli ping
   
   # Start Redis if not running
   redis-server
   ```

2. **Out of Memory**
   ```bash
   # Check Redis memory usage
   redis-cli INFO memory
   
   # Clear cache if needed
   redis-cli FLUSHALL
   ```

3. **Performance Issues**
   ```bash
   # Monitor slow queries
   redis-cli --latency
   
   # Check for blocking operations
   redis-cli --latency-history
   ```

### Debug Mode
```python
# Enable cache debug logging
logging.getLogger('astro_engine.cache_manager').setLevel(logging.DEBUG)
```

## Maintenance

### Regular Tasks
1. Monitor memory usage
2. Check error rates
3. Review cache hit rates
4. Clean up expired keys
5. Backup Redis data (if persistence enabled)

### Cache Warming
```python
# Warm cache with common calculations
python3 -c "
from astro_engine.cache_manager import warm_cache
warm_cache()
"
```

## Next Steps

After Redis implementation (Phase 1), proceed with:
1. **Phase 2**: Prometheus Metrics Implementation
2. **Phase 3**: Structured Logging
3. **Phase 4**: Celery Task Queue

---

*Generated: 2025-06-23*  
*Version: 1.0*  
*Status: Phase 1 Complete*
