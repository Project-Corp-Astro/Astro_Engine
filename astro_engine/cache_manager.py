# # Redis Cache Manager for Astro Engine Performance Enhancement
# # Phase 1.1: Redis Client Setup and Cache Utilities

# import redis
# import json
# import hashlib
# import logging
# from functools import wraps
# from typing import Dict, Any, Optional, Union
# from flask import request, current_app, jsonify, Response
# import time
# import os
# from datetime import datetime, timedelta

# class AstroCacheManager:
#     """
#     Centralized cache management for Astro Engine calculations
#     Implements Redis caching with performance monitoring and health checks
#     """
    
#     def __init__(self, app=None):
#         self.redis_client = None
#         self.stats = {
#             'cache_hits': 0,
#             'cache_misses': 0,
#             'cache_errors': 0,
#             'total_operations': 0
#         }
#         self.logger = logging.getLogger(__name__)
        
#         if app:
#             self.init_app(app)
    
#     def init_app(self, app):
#         """Initialize Redis connection with Flask app"""
#         try:
#             redis_url = app.config.get('REDIS_URL', os.getenv('REDIS_URL', 'redis://default:ld7dfWRq3s78EIDW3QXwnqhzPuZDNvbo@redis-14832.c61.us-east-1-3.ec2.redns.redis-cloud.com:14832'))
            
#             self.redis_client = redis.Redis.from_url(
#                 redis_url,
#                 decode_responses=True,
#                 socket_timeout=5,
#                 socket_connect_timeout=5,
#                 retry_on_timeout=True,
#                 max_connections=20
#             )
            
#             # Test Redis connection
#             self.redis_client.ping()
#             self.logger.info(f"✅ Redis connected successfully: {redis_url}")
            
#             # Set default TTL from config
#             self.default_ttl = int(app.config.get('CACHE_DEFAULT_TIMEOUT', 3600))
            
#         except Exception as e:
#             self.logger.error(f"❌ Redis connection failed: {e}")
#             self.redis_client = None
    
#     def is_available(self) -> bool:
#         """Check if Redis is available and healthy"""
#         try:
#             if self.redis_client:
#                 self.redis_client.ping()
#                 return True
#         except Exception as e:
#             self.logger.warning(f"Redis health check failed: {e}")
#         return False
    
#     def generate_cache_key(self, data: Dict[str, Any], prefix: str = "calc") -> str:
#         """
#         Generate consistent cache key from birth data
#         Ensures same inputs always generate same key
#         """
#         try:
#             # Normalize data for consistent key generation
#             cache_data = {
#                 'birth_date': data.get('birth_date', ''),
#                 'birth_time': data.get('birth_time', ''),
#                 'latitude': round(float(data.get('latitude', 0)), 6),
#                 'longitude': round(float(data.get('longitude', 0)), 6),
#                 'timezone_offset': float(data.get('timezone_offset', 0)),
#                 'ayanamsa': data.get('ayanamsa', 'lahiri'),
#                 'calculation_type': data.get('calculation_type', 'natal')
#             }
            
#             # Create deterministic hash
#             key_string = json.dumps(cache_data, sort_keys=True)
#             hash_key = hashlib.md5(key_string.encode()).hexdigest()
            
#             return f"{prefix}:{hash_key}"
            
#         except Exception as e:
#             self.logger.error(f"Cache key generation failed: {e}")
#             # Fallback to timestamp-based key
#             return f"{prefix}:fallback:{int(time.time())}"
    
#     def get(self, key: str) -> Optional[Any]:
#         """Get value from cache with metrics tracking"""
#         start_time = time.time()
        
#         if not self.is_available():
#             self.stats['cache_errors'] += 1
#             # Record metrics if available
#             if hasattr(current_app, 'metrics_manager'):
#                 current_app.metrics_manager.record_cache_operation('get', 'error')
#                 current_app.metrics_manager.record_cache_performance('get', time.time() - start_time)
#             # Log with structured logger
#             if hasattr(current_app, 'structured_logger'):
#                 current_app.structured_logger.log_cache_operation('get', key, 'error', time.time() - start_time)
#             return None
        
#         try:
#             value = self.redis_client.get(key)
#             duration = time.time() - start_time
            
#             if value is not None:
#                 self.stats['cache_hits'] += 1
#                 self.logger.debug(f"🟢 Cache HIT: {key} ({duration:.3f}s)")
#                 # Record metrics
#                 if hasattr(current_app, 'metrics_manager'):
#                     current_app.metrics_manager.record_cache_operation('get', 'hit')
#                     current_app.metrics_manager.record_cache_performance('get', duration)
#                 # Structured logging
#                 if hasattr(current_app, 'structured_logger'):
#                     current_app.structured_logger.log_cache_operation('get', key, 'hit', duration)
#                 return json.loads(value)
#             else:
#                 self.stats['cache_misses'] += 1
#                 self.logger.debug(f"⚪ Cache MISS: {key} ({duration:.3f}s)")
#                 # Record metrics
#                 if hasattr(current_app, 'metrics_manager'):
#                     current_app.metrics_manager.record_cache_operation('get', 'miss')
#                     current_app.metrics_manager.record_cache_performance('get', duration)
#                 # Structured logging
#                 if hasattr(current_app, 'structured_logger'):
#                     current_app.structured_logger.log_cache_operation('get', key, 'miss', duration)
#                 return None
                
#         except Exception as e:
#             duration = time.time() - start_time
#             self.stats['cache_errors'] += 1
#             self.logger.error(f"Cache get error for key {key}: {e}")
#             # Record metrics
#             if hasattr(current_app, 'metrics_manager'):
#                 current_app.metrics_manager.record_cache_operation('get', 'error')
#                 current_app.metrics_manager.record_cache_performance('get', duration)
#             # Structured logging
#             if hasattr(current_app, 'structured_logger'):
#                 current_app.structured_logger.log_error('CacheError', f"Cache get failed: {e}", 
#                                                        {'operation': 'get', 'key': key, 'duration': duration}, e)
#             return None

#     def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
#         """Set value in cache with metrics tracking"""
#         start_time = time.time()
        
#         if not self.is_available():
#             self.stats['cache_errors'] += 1
#             # Record metrics if available
#             if hasattr(current_app, 'metrics_manager'):
#                 current_app.metrics_manager.record_cache_operation('set', 'error')
#                 current_app.metrics_manager.record_cache_performance('set', time.time() - start_time)
#             return False
        
#         try:
#             # Serialize value
#             serialized_value = json.dumps(value)
            
#             # Set with TTL
#             if ttl:
#                 success = self.redis_client.setex(key, ttl, serialized_value)
#             else:
#                 success = self.redis_client.set(key, serialized_value)
            
#             duration = time.time() - start_time
            
#             if success:
#                 self.logger.debug(f"🟢 Cache SET: {key} (TTL: {ttl}s, {duration:.3f}s)")
#                 # Record metrics
#                 if hasattr(current_app, 'metrics_manager'):
#                     current_app.metrics_manager.record_cache_operation('set', 'success')
#                     current_app.metrics_manager.record_cache_performance('set', duration)
#                 return True
#             else:
#                 self.stats['cache_errors'] += 1
#                 # Record metrics
#                 if hasattr(current_app, 'metrics_manager'):
#                     current_app.metrics_manager.record_cache_operation('set', 'error')
#                     current_app.metrics_manager.record_cache_performance('set', duration)
#                 return False
                
#         except Exception as e:
#             duration = time.time() - start_time
#             self.stats['cache_errors'] += 1
#             self.logger.error(f"Cache set error for key {key}: {e}")
#             # Record metrics
#             if hasattr(current_app, 'metrics_manager'):
#                 current_app.metrics_manager.record_cache_operation('set', 'error')
#                 current_app.metrics_manager.record_cache_performance('set', duration)
#             return False
    
#     def delete(self, pattern: str) -> int:
#         """Delete cache entries matching pattern"""
#         if not self.is_available():
#             return 0
            
#         try:
#             keys = self.redis_client.keys(pattern)
#             if keys:
#                 deleted = self.redis_client.delete(*keys)
#                 self.logger.info(f"🗑️ Deleted {deleted} cache entries: {pattern}")
#                 return deleted
#             return 0
            
#         except Exception as e:
#             self.logger.error(f"Cache delete error for pattern {pattern}: {e}")
#             return 0
    
#     def get_stats(self) -> Dict[str, Any]:
#         """Get comprehensive cache statistics"""
#         stats = self.stats.copy()
        
#         # Calculate hit rate
#         total_gets = stats['cache_hits'] + stats['cache_misses']
#         stats['hit_rate'] = (stats['cache_hits'] / max(total_gets, 1)) * 100
        
#         # Add Redis availability status
#         stats['redis_available'] = self.is_available()
        
#         # Get Redis info if available
#         if self.is_available():
#             try:
#                 redis_info = self.redis_client.info()
#                 stats['redis_info'] = {
#                     'used_memory': redis_info.get('used_memory_human', 'N/A'),
#                     'total_keys': redis_info.get('db0', {}).get('keys', 0) if 'db0' in redis_info else 0,
#                     'hits': redis_info.get('keyspace_hits', 0),
#                     'misses': redis_info.get('keyspace_misses', 0),
#                     'connected_clients': redis_info.get('connected_clients', 0)
#                 }
#             except Exception as e:
#                 stats['redis_info'] = {'error': str(e)}
#         else:
#             stats['redis_info'] = {'status': 'unavailable'}
        
#         return stats
    
#     def clear_all(self) -> bool:
#         """Clear all cache entries (use with caution)"""
#         if not self.is_available():
#             return False
            
#         try:
#             self.redis_client.flushdb()
#             self.logger.warning("🧹 All cache entries cleared")
#             return True
#         except Exception as e:
#             self.logger.error(f"Cache clear all error: {e}")
#             return False


# def cache_calculation(cache_prefix: str, ttl: Optional[int] = None):
#     """
#     Decorator for caching expensive astrological calculations
    
#     Args:
#         cache_prefix: Prefix for cache keys (e.g., 'natal', 'navamsa')
#         ttl: Time to live in seconds (optional)
    
#     Usage:
#         @cache_calculation('natal_chart', ttl=86400)
#         def calculate_natal_chart():
#             # expensive calculation
#             return result
#     """
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             try:
#                 # Get cache manager from app context
#                 cache_manager = getattr(current_app, 'cache_manager', None)
#                 current_app.logger.debug(f"Cache decorator called for {func.__name__}, cache_manager: {cache_manager is not None}")
                
#                 if not cache_manager:
#                     current_app.logger.error(f"No cache_manager found in current_app for {func.__name__}")
#                     return func(*args, **kwargs)
                
#                 if not cache_manager.is_available():
#                     current_app.logger.warning(f"Cache manager not available for {func.__name__}")
#                     return func(*args, **kwargs)
                
#                 # Get request data for cache key generation
#                 data = request.get_json() or {}
#                 cache_key = cache_manager.generate_cache_key(data, cache_prefix)
#                 current_app.logger.debug(f"Generated cache key: {cache_key}")
                
#                 # Try to get from cache first
#                 cached_result = cache_manager.get(cache_key)
#                 if cached_result:
#                     current_app.logger.info(f"Cache HIT for {func.__name__}")
#                     # Add cache metadata to cached result
#                     if isinstance(cached_result, dict):
#                         cached_result['_performance'] = {
#                             'cached': True,
#                             'timestamp': datetime.utcnow().isoformat()
#                         }
#                     return jsonify(cached_result)
                
#                 # Calculate result if not cached
#                 current_app.logger.info(f"Cache MISS for {func.__name__}, calculating...")
#                 start_time = time.time()
#                 result = func(*args, **kwargs)
#                 calculation_time = time.time() - start_time
                
#                 # Handle Flask Response objects
#                 if isinstance(result, Response):
#                     # Extract JSON data from the Response
#                     try:
#                         json_data = result.get_json()
#                         if json_data and isinstance(json_data, dict):
#                             # Add performance metadata
#                             json_data['_performance'] = {
#                                 'calculation_time': round(calculation_time, 3),
#                                 'cached': False,
#                                 'timestamp': datetime.utcnow().isoformat()
#                             }
                            
#                             # Store in cache (store the dict, not the Response)
#                             success = cache_manager.set(cache_key, json_data, ttl)
#                             current_app.logger.debug(f"Cache SET for {func.__name__}: {success}")
                            
#                             # Return updated Response
#                             return jsonify(json_data)
#                         else:
#                             current_app.logger.warning(f"Could not extract JSON from Response for {func.__name__}")
#                             return result
#                     except Exception as e:
#                         current_app.logger.error(f"Error extracting JSON from Response for {func.__name__}: {e}")
#                         return result
                
#                 # Handle dict responses (shouldn't happen with current routes but good to have)
#                 elif isinstance(result, dict):
#                     # Add performance metadata
#                     result['_performance'] = {
#                         'calculation_time': round(calculation_time, 3),
#                         'cached': False,
#                         'timestamp': datetime.utcnow().isoformat()
#                     }
                    
#                     # Store in cache
#                     success = cache_manager.set(cache_key, result, ttl)
#                     current_app.logger.debug(f"Cache SET for {func.__name__}: {success}")
                    
#                     return jsonify(result)
                
#                 else:
#                     current_app.logger.warning(f"Unexpected result type for {func.__name__}: {type(result)}")
#                     return result
                
#             except Exception as e:
#                 current_app.logger.error(f"Cache decorator error in {func.__name__}: {e}")
#                 # Always return the function result, even if caching fails
#                 return func(*args, **kwargs)
        
#         return wrapper
#     return decorator


# def create_cache_manager(app):
#     """Factory function to create and configure cache manager"""
#     cache_manager = AstroCacheManager(app)
#     app.cache_manager = cache_manager
#     return cache_manager











# /////////////////////////////////////////////////////////////////////////////////////
#    # End of Astro Engine Cache Manager Code With out redis 
# AstroCacheManager: Cache Skeleton (No Redis backend, plug-compatible)
import json
import hashlib
import logging
from functools import wraps
from typing import Dict, Any, Optional, Union
from flask import request, current_app, jsonify, Response
import time
from datetime import datetime, timedelta

class AstroCacheManager:
    """
    Centralized cache management for Astro Engine calculations.
    No Redis or backend storage—acts as a pass-through (stub).
    Keeps metrics, logs, cache key generation for future extension.
    """
    def __init__(self, app=None):
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_errors': 0,
            'total_operations': 0
        }
        self.logger = logging.getLogger(__name__)
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize cache manager (no Redis)"""
        # self.logger.info("✅ AstroCacheManager initialized (no Redis backend)")
        self.default_ttl = int(getattr(app, 'config', {}).get('CACHE_DEFAULT_TIMEOUT', 3600))
    
    def is_available(self) -> bool:
        """Always returns False (no backend). Used for plug-compatibility."""
        return False
    
    def generate_cache_key(self, data: Dict[str, Any], prefix: str = "calc") -> str:
        """
        Generate consistent cache key from birth data
        Ensures same inputs always generate same key
        """
        try:
            cache_data = {
                'birth_date': data.get('birth_date', ''),
                'birth_time': data.get('birth_time', ''),
                'latitude': round(float(data.get('latitude', 0)), 6),
                'longitude': round(float(data.get('longitude', 0)), 6),
                'timezone_offset': float(data.get('timezone_offset', 0)),
                'ayanamsa': data.get('ayanamsa', 'lahiri'),
                'calculation_type': data.get('calculation_type', 'natal')
            }
            key_string = json.dumps(cache_data, sort_keys=True)
            hash_key = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{hash_key}"
        except Exception as e:
            self.logger.error(f"Cache key generation failed: {e}")
            return f"{prefix}:fallback:{int(time.time())}"
    
    def get(self, key: str) -> Optional[Any]:
        """Stub cache get: Always returns None (no backend)"""
        self.stats['cache_misses'] += 1
        # Metrics/logging are still tracked for future backend plug-in
        if hasattr(current_app, 'metrics_manager'):
            current_app.metrics_manager.record_cache_operation('get', 'miss')
        if hasattr(current_app, 'structured_logger'):
            current_app.structured_logger.log_cache_operation('get', key, 'miss', 0)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stub cache set: No operation (no backend)"""
        # Pretend to store, do nothing
        if hasattr(current_app, 'metrics_manager'):
            current_app.metrics_manager.record_cache_operation('set', 'noop')
        return False

    def delete(self, pattern: str) -> int:
        """Stub cache delete: Does nothing"""
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Return cache stats (all zeros except misses, no backend info)"""
        stats = self.stats.copy()
        total_gets = stats['cache_hits'] + stats['cache_misses']
        stats['hit_rate'] = (stats['cache_hits'] / max(total_gets, 1)) * 100
        
        return stats
    
    def clear_all(self) -> bool:
        """Stub clear: Does nothing"""
        return False

def cache_calculation(cache_prefix: str, ttl: Optional[int] = None):
    """
    Decorator for caching expensive astrological calculations.
    Here, just runs the function—cache always bypassed (for compatibility).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                cache_manager = getattr(current_app, 'cache_manager', None)
                current_app.logger.debug(f"Cache decorator called for {func.__name__}, cache_manager: {cache_manager is not None}")
                if not cache_manager or not cache_manager.is_available():
                    current_app.logger.warning(f"Cache manager not available for {func.__name__} (no backend)")
                    return func(*args, **kwargs)
                # Never runs below since is_available() is always False
            except Exception as e:
                current_app.logger.error(f"Cache decorator error in {func.__name__}: {e}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def create_cache_manager(app):
    """Factory function to create and configure cache manager (no Redis)"""
    cache_manager = AstroCacheManager(app)
    app.cache_manager = cache_manager
    return cache_manager
