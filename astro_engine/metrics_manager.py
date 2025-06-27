# # Prometheus Metrics Manager for Astro Engine
# # Phase 2.1: Prometheus Setup and Metrics Collection Framework

# import time
# import os
# import logging
# from functools import wraps
# from typing import Dict, Any, Optional, Callable
# from datetime import datetime
# from flask import request, current_app

# from prometheus_client import (
#     Counter, Histogram, Gauge, Summary, Info,
#     CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
#     multiprocess, REGISTRY
# )

# class AstroMetricsManager:
#     """
#     Centralized metrics management for Astro Engine
#     Implements Prometheus metrics collection with comprehensive monitoring
#     """
    
#     _instance = None
#     _initialized = False
    
#     def __new__(cls, app=None):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance
    
#     def __init__(self, app=None):
#         if self._initialized:
#             return
            
#         self.logger = logging.getLogger(__name__)
        
#         # Initialize metrics only once
#         self._init_metrics()
#         self._initialized = True
        
#         if app:
#             self.init_app(app)
    
#     def _init_metrics(self):
#         """Initialize all Prometheus metrics"""
        
#         # Application Info
#         self.app_info = Info(
#             'astro_engine_info',
#             'Astro Engine application information'
#         )
        
#         # Request Metrics
#         self.request_count = Counter(
#             'astro_engine_requests_total',
#             'Total number of HTTP requests',
#             ['method', 'endpoint', 'status_code']
#         )
        
#         self.request_duration = Histogram(
#             'astro_engine_request_duration_seconds',
#             'HTTP request duration in seconds',
#             ['method', 'endpoint'],
#             buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
#         )
        
#         self.request_size = Summary(
#             'astro_engine_request_size_bytes',
#             'HTTP request size in bytes',
#             ['method', 'endpoint']
#         )
        
#         self.response_size = Summary(
#             'astro_engine_response_size_bytes',
#             'HTTP response size in bytes',
#             ['method', 'endpoint']
#         )
        
#         # Cache Metrics
#         self.cache_operations = Counter(
#             'astro_engine_cache_operations_total',
#             'Total cache operations',
#             ['operation', 'result']  # operation: get/set/delete, result: hit/miss/error
#         )
        
#         self.cache_hit_rate = Gauge(
#             'astro_engine_cache_hit_rate',
#             'Current cache hit rate percentage'
#         )
        
#         self.cache_size = Gauge(
#             'astro_engine_cache_size_bytes',
#             'Current cache size in bytes'
#         )
        
#         # Calculation Metrics
#         self.calculation_duration = Histogram(
#             'astro_engine_calculation_duration_seconds',
#             'Astrological calculation duration in seconds',
#             ['calculation_type'],
#             buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
#         )
        
#         self.calculation_count = Counter(
#             'astro_engine_calculations_total',
#             'Total number of calculations performed',
#             ['calculation_type', 'cached']
#         )
        
#         # Swiss Ephemeris Metrics
#         self.ephemeris_access = Counter(
#             'astro_engine_ephemeris_access_total',
#             'Total Swiss Ephemeris file accesses',
#             ['file_type']
#         )
        
#         # Error Metrics
#         self.error_count = Counter(
#             'astro_engine_errors_total',
#             'Total number of errors',
#             ['error_type', 'endpoint']
#         )
        
#         # Concurrent Users
#         self.active_requests = Gauge(
#             'astro_engine_active_requests',
#             'Number of currently active requests'
#         )
        
#         # System Metrics
#         self.memory_usage = Gauge(
#             'astro_engine_memory_usage_bytes',
#             'Current memory usage in bytes'
#         )
        
#         self.redis_connections = Gauge(
#             'astro_engine_redis_connections',
#             'Number of Redis connections'
#         )
        
#         # Business Metrics
#         self.user_sessions = Counter(
#             'astro_engine_user_sessions_total',
#             'Total number of user sessions',
#             ['user_type']
#         )
        
#         self.chart_requests = Counter(
#             'astro_engine_chart_requests_total',
#             'Total chart calculation requests',
#             ['chart_type', 'ayanamsa']
#         )
        
#         # Advanced Performance Metrics (Phase 2.2)
#         self.database_query_duration = Histogram(
#             'astro_engine_database_query_duration_seconds',
#             'Database query execution time',
#             ['query_type'],
#             buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
#         )
        
#         self.api_response_time_percentiles = Summary(
#             'astro_engine_api_response_time_seconds',
#             'API response time percentiles',
#             ['endpoint', 'status']
#         )
        
#         self.concurrent_users_active = Gauge(
#             'astro_engine_concurrent_users_active',
#             'Current number of active concurrent users'
#         )
        
#         self.cache_performance = Summary(
#             'astro_engine_cache_performance_seconds',
#             'Cache operation performance metrics',
#             ['operation_type']
#         )
        
#         # Swiss Ephemeris Performance
#         self.ephemeris_calculation_time = Histogram(
#             'astro_engine_ephemeris_calculation_seconds',
#             'Swiss Ephemeris calculation time',
#             ['calculation_type'],
#             buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
#         )
        
#         self.ephemeris_file_reads = Counter(
#             'astro_engine_ephemeris_file_reads_total',
#             'Total Swiss Ephemeris file read operations',
#             ['file_name', 'status']
#         )
        
#         # Advanced Business Metrics
#         self.calculation_complexity = Histogram(
#             'astro_engine_calculation_complexity',
#             'Calculation complexity score',
#             ['chart_type'],
#             buckets=[1, 5, 10, 25, 50, 100, 250, 500]
#         )
        
#         self.user_interaction_rate = Counter(
#             'astro_engine_user_interactions_total',
#             'User interaction events',
#             ['interaction_type', 'endpoint']
#         )
        
#         self.error_rate_percentage = Gauge(
#             'astro_engine_error_rate_percentage',
#             'Current error rate as percentage'
#         )
        
#         self.peak_concurrent_users = Gauge(
#             'astro_engine_peak_concurrent_users',
#             'Peak concurrent users in current session'
#         )
        
#         # Resource Utilization
#         self.cpu_usage_percentage = Gauge(
#             'astro_engine_cpu_usage_percentage',
#             'Current CPU usage percentage'
#         )
        
#         self.memory_usage_percentage = Gauge(
#             'astro_engine_memory_usage_percentage',
#             'Current memory usage percentage'
#         )
        
#         self.redis_memory_usage = Gauge(
#             'astro_engine_redis_memory_bytes',
#             'Redis memory usage in bytes'
#         )
    
#     def init_app(self, app):
#         """Initialize metrics with Flask app"""
#         app.metrics_manager = self
        
#         # Set application info
#         self.app_info.info({
#             'version': app.config.get('VERSION', '1.3.0'),
#             'environment': app.config.get('ENVIRONMENT', 'development'),
#             'python_version': os.sys.version,
#             'start_time': datetime.utcnow().isoformat()
#         })
        
#         # Register request handlers
#         app.before_request(self._before_request)
#         app.after_request(self._after_request)
        
#         self.logger.info("🔥 Prometheus metrics manager initialized")
    
#     def _before_request(self):
#         """Called before each request"""
#         request.start_time = time.time()
#         self.active_requests.inc()
    
#     def _after_request(self, response):
#         """Called after each request"""
#         # Calculate request duration
#         duration = time.time() - getattr(request, 'start_time', time.time())
        
#         # Get endpoint info
#         endpoint = request.endpoint or 'unknown'
#         method = request.method
#         status_code = str(response.status_code)
        
#         # Update metrics
#         self.request_count.labels(
#             method=method,
#             endpoint=endpoint,
#             status_code=status_code
#         ).inc()
        
#         self.request_duration.labels(
#             method=method,
#             endpoint=endpoint
#         ).observe(duration)
        
#         # Request/Response size
#         if hasattr(request, 'content_length') and request.content_length:
#             self.request_size.labels(
#                 method=method,
#                 endpoint=endpoint
#             ).observe(request.content_length)
        
#         if response.content_length:
#             self.response_size.labels(
#                 method=method,
#                 endpoint=endpoint
#             ).observe(response.content_length)
        
#         # Decrement active requests
#         self.active_requests.dec()
        
#         return response
    
#     def record_cache_operation(self, operation: str, result: str):
#         """Record cache operation metrics"""
#         self.cache_operations.labels(
#             operation=operation,
#             result=result
#         ).inc()
    
#     def update_cache_hit_rate(self, hit_rate: float):
#         """Update cache hit rate gauge"""
#         self.cache_hit_rate.set(hit_rate)
    
#     def record_calculation(self, calc_type: str, duration: float, cached: bool = False):
#         """Record calculation metrics"""
#         self.calculation_duration.labels(
#             calculation_type=calc_type
#         ).observe(duration)
        
#         self.calculation_count.labels(
#             calculation_type=calc_type,
#             cached=str(cached).lower()
#         ).inc()
    
#     def record_chart_request(self, chart_type: str, ayanamsa: str = 'lahiri'):
#         """Record chart request metrics"""
#         self.chart_requests.labels(
#             chart_type=chart_type,
#             ayanamsa=ayanamsa
#         ).inc()
    
#     def record_error(self, error_type: str, endpoint: str = 'unknown'):
#         """Record error metrics"""
#         self.error_count.labels(
#             error_type=error_type,
#             endpoint=endpoint
#         ).inc()
    
#     def record_ephemeris_access(self, file_type: str = 'se1'):
#         """Record Swiss Ephemeris file access"""
#         self.ephemeris_access.labels(
#             file_type=file_type
#         ).inc()
    
#     def update_system_metrics(self):
#         """Update system-level metrics"""
#         try:
#             import psutil
#             process = psutil.Process()
#             self.memory_usage.set(process.memory_info().rss)
#         except ImportError:
#             # Fallback if psutil not available
#             import resource
#             self.memory_usage.set(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
#         except Exception as e:
#             self.logger.error(f"Error updating system metrics: {e}")
    
#     def update_redis_metrics(self, cache_manager):
#         """Update Redis-related metrics"""
#         try:
#             if cache_manager and cache_manager.is_available():
#                 redis_info = cache_manager.redis_client.info()
#                 self.redis_connections.set(redis_info.get('connected_clients', 0))
                
#                 # Update cache metrics
#                 stats = cache_manager.get_stats()
#                 self.update_cache_hit_rate(stats.get('hit_rate', 0))
                
#                 # Estimate cache size from Redis memory
#                 redis_memory = redis_info.get('used_memory', 0)
#                 self.cache_size.set(redis_memory)
#                 self.redis_memory_usage.set(redis_memory)
#         except Exception as e:
#             self.logger.error(f"Error updating Redis metrics: {e}")
    
#     # Advanced Metrics Methods (Phase 2.2)
    
#     def record_database_query(self, query_type: str, duration: float):
#         """Record database query performance"""
#         self.database_query_duration.labels(query_type=query_type).observe(duration)
    
#     def record_api_response_time(self, endpoint: str, status: str, duration: float):
#         """Record API response time for percentile tracking"""
#         self.api_response_time_percentiles.labels(
#             endpoint=endpoint,
#             status=status
#         ).observe(duration)
    
#     def update_concurrent_users(self, count: int):
#         """Update current concurrent users count"""
#         self.concurrent_users_active.set(count)
        
#         # Track peak - safely get current peak value
#         try:
#             current_peak = 0
#             if hasattr(self.peak_concurrent_users, '_value'):
#                 if hasattr(self.peak_concurrent_users._value, '_value'):
#                     current_peak = self.peak_concurrent_users._value._value
#                 else:
#                     current_peak = self.peak_concurrent_users._value
                    
#             if count > current_peak:
#                 self.peak_concurrent_users.set(count)
#         except Exception as e:
#             self.logger.error(f"Error updating peak concurrent users: {e}")
#             # Just set the peak to current count as fallback
#             self.peak_concurrent_users.set(count)
    
#     def record_cache_performance(self, operation_type: str, duration: float):
#         """Record cache operation performance"""
#         self.cache_performance.labels(operation_type=operation_type).observe(duration)
    
#     def record_ephemeris_calculation(self, calc_type: str, duration: float):
#         """Record Swiss Ephemeris calculation time"""
#         self.ephemeris_calculation_time.labels(
#             calculation_type=calc_type
#         ).observe(duration)
    
#     def record_ephemeris_file_read(self, file_name: str, status: str = 'success'):
#         """Record Swiss Ephemeris file read operation"""
#         self.ephemeris_file_reads.labels(
#             file_name=file_name,
#             status=status
#         ).inc()
    
#     def record_calculation_complexity(self, chart_type: str, complexity_score: int):
#         """Record calculation complexity score"""
#         self.calculation_complexity.labels(chart_type=chart_type).observe(complexity_score)
    
#     def record_user_interaction(self, interaction_type: str, endpoint: str):
#         """Record user interaction events"""
#         self.user_interaction_rate.labels(
#             interaction_type=interaction_type,
#             endpoint=endpoint
#         ).inc()
    
#     def update_error_rate(self, percentage: float):
#         """Update current error rate percentage"""
#         self.error_rate_percentage.set(percentage)
    
#     def update_resource_utilization(self):
#         """Update CPU and memory utilization metrics"""
#         try:
#             import psutil
            
#             # CPU usage
#             cpu_percent = psutil.cpu_percent(interval=1)
#             self.cpu_usage_percentage.set(cpu_percent)
            
#             # Memory usage
#             memory = psutil.virtual_memory()
#             self.memory_usage_percentage.set(memory.percent)
            
#             # Process-specific memory
#             process = psutil.Process()
#             process_memory = process.memory_info().rss
#             self.memory_usage.set(process_memory)
            
#         except ImportError:
#             # Fallback without psutil
#             import resource
#             process_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
#             self.memory_usage.set(process_memory)
#         except Exception as e:
#             self.logger.error(f"Error updating resource utilization: {e}")
    
#     def calculate_and_update_error_rate(self):
#         """Calculate and update error rate from request metrics"""
#         try:
#             # Get total requests and error requests from metrics
#             total_requests = 0
#             error_requests = 0
            
#             for metric in self.request_count.collect():
#                 for sample in metric.samples:
#                     total_requests += sample.value
#                     if sample.labels.get('status_code', '').startswith(('4', '5')):
#                         error_requests += sample.value
            
#             if total_requests > 0:
#                 error_rate = (error_requests / total_requests) * 100
#                 self.update_error_rate(error_rate)
            
#         except Exception as e:
#             self.logger.error(f"Error calculating error rate: {e}")
    
#     def get_performance_summary(self) -> Dict[str, Any]:
#         """Get comprehensive performance summary"""
#         try:
#             # Helper function to safely get gauge value
#             def safe_get_gauge_value(gauge):
#                 try:
#                     # Try different ways to get the gauge value
#                     if hasattr(gauge, '_value') and hasattr(gauge._value, '_value'):
#                         return gauge._value._value
#                     elif hasattr(gauge, '_value'):
#                         return gauge._value
#                     else:
#                         return 0.0
#                 except:
#                     return 0.0
            
#             summary = {
#                 'timestamp': datetime.utcnow().isoformat(),
#                 'active_requests': safe_get_gauge_value(self.active_requests),
#                 'concurrent_users': safe_get_gauge_value(self.concurrent_users_active),
#                 'peak_concurrent_users': safe_get_gauge_value(self.peak_concurrent_users),
#                 'cache_hit_rate': safe_get_gauge_value(self.cache_hit_rate),
#                 'error_rate_percentage': safe_get_gauge_value(self.error_rate_percentage),
#                 'memory_usage_mb': safe_get_gauge_value(self.memory_usage) / (1024 * 1024),
#                 'cpu_usage_percentage': safe_get_gauge_value(self.cpu_usage_percentage),
#                 'redis_connections': safe_get_gauge_value(self.redis_connections),
#                 'redis_memory_mb': safe_get_gauge_value(self.redis_memory_usage) / (1024 * 1024)
#             }
#             return summary
#         except Exception as e:
#             self.logger.error(f"Error generating performance summary: {e}")
#             return {
#                 'timestamp': datetime.utcnow().isoformat(),
#                 'error': f"Failed to generate summary: {e}"
#             }
    
#     def get_metrics(self) -> str:
#         """Get Prometheus metrics in text format"""
#         try:
#             return generate_latest(REGISTRY)
#         except Exception as e:
#             self.logger.error(f"Error generating metrics: {e}")
#             return ""


# def metrics_decorator(calculation_type: str):
#     """
#     Decorator to automatically track calculation metrics
    
#     Usage:
#         @metrics_decorator('natal_chart')
#         def calculate_natal_chart():
#             # calculation logic
#             return result
#     """
#     def decorator(func: Callable) -> Callable:
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             start_time = time.time()
            
#             try:
#                 result = func(*args, **kwargs)
#                 duration = time.time() - start_time
                
#                 # Get metrics manager from app context
#                 if hasattr(current_app, 'metrics_manager'):
#                     metrics_manager = current_app.metrics_manager
                    
#                     # Check if result was cached
#                     cached = False
#                     if hasattr(result, 'get_json'):
#                         # Flask Response object
#                         try:
#                             json_data = result.get_json()
#                             if json_data and isinstance(json_data, dict):
#                                 perf_data = json_data.get('_performance', {})
#                                 cached = perf_data.get('cached', False)
#                         except:
#                             pass
#                     elif isinstance(result, dict):
#                         perf_data = result.get('_performance', {})
#                         cached = perf_data.get('cached', False)
                    
#                     metrics_manager.record_calculation(calculation_type, duration, cached)
                
#                 return result
                
#             except Exception as e:
#                 duration = time.time() - start_time
                
#                 # Record error
#                 if hasattr(current_app, 'metrics_manager'):
#                     endpoint = getattr(request, 'endpoint', 'unknown')
#                     current_app.metrics_manager.record_error(
#                         error_type=type(e).__name__,
#                         endpoint=endpoint
#                     )
                
#                 raise e
        
#         return wrapper
#     return decorator


# def create_metrics_manager(app):
#     """Factory function to create and configure metrics manager"""
#     # Check if metrics manager already exists
#     if hasattr(app, 'metrics_manager'):
#         return app.metrics_manager
        
#     metrics_manager = AstroMetricsManager(app)
#     return metrics_manager






# /////////////////////////////////////////////////////////////////////////////
#   # End of Astro Engine Metrics Manager with out redis .
# Prometheus Metrics Manager for Astro Engine
# Phase 2.1: Prometheus Setup and Metrics Collection Framework

import time
import os
import logging
from functools import wraps
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from flask import request, current_app

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    multiprocess, REGISTRY
)

class AstroMetricsManager:
    """
    Centralized metrics management for Astro Engine
    Implements Prometheus metrics collection with comprehensive monitoring
    (No Redis metrics)
    """

    _instance = None
    _initialized = False

    def __new__(cls, app=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, app=None):
        if self._initialized:
            return

        self.logger = logging.getLogger(__name__)

        # Initialize metrics only once
        self._init_metrics()
        self._initialized = True

        if app:
            self.init_app(app)

    def _init_metrics(self):
        """Initialize all Prometheus metrics"""

        # Application Info
        self.app_info = Info(
            'astro_engine_info',
            'Astro Engine application information'
        )

        # Request Metrics
        self.request_count = Counter(
            'astro_engine_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status_code']
        )

        self.request_duration = Histogram(
            'astro_engine_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )

        self.request_size = Summary(
            'astro_engine_request_size_bytes',
            'HTTP request size in bytes',
            ['method', 'endpoint']
        )

        self.response_size = Summary(
            'astro_engine_response_size_bytes',
            'HTTP response size in bytes',
            ['method', 'endpoint']
        )

        # Cache Metrics
        self.cache_operations = Counter(
            'astro_engine_cache_operations_total',
            'Total cache operations',
            ['operation', 'result']  # operation: get/set/delete, result: hit/miss/error
        )

        self.cache_hit_rate = Gauge(
            'astro_engine_cache_hit_rate',
            'Current cache hit rate percentage'
        )

        self.cache_size = Gauge(
            'astro_engine_cache_size_bytes',
            'Current cache size in bytes'
        )

        # Calculation Metrics
        self.calculation_duration = Histogram(
            'astro_engine_calculation_duration_seconds',
            'Astrological calculation duration in seconds',
            ['calculation_type'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )

        self.calculation_count = Counter(
            'astro_engine_calculations_total',
            'Total number of calculations performed',
            ['calculation_type', 'cached']
        )

        # Swiss Ephemeris Metrics
        self.ephemeris_access = Counter(
            'astro_engine_ephemeris_access_total',
            'Total Swiss Ephemeris file accesses',
            ['file_type']
        )

        # Error Metrics
        self.error_count = Counter(
            'astro_engine_errors_total',
            'Total number of errors',
            ['error_type', 'endpoint']
        )

        # Concurrent Users
        self.active_requests = Gauge(
            'astro_engine_active_requests',
            'Number of currently active requests'
        )

        # System Metrics
        self.memory_usage = Gauge(
            'astro_engine_memory_usage_bytes',
            'Current memory usage in bytes'
        )

        # Removed Redis metrics below:
        # self.redis_connections = Gauge(
        #     'astro_engine_redis_connections',
        #     'Number of Redis connections'
        # )

        # Business Metrics
        self.user_sessions = Counter(
            'astro_engine_user_sessions_total',
            'Total number of user sessions',
            ['user_type']
        )

        self.chart_requests = Counter(
            'astro_engine_chart_requests_total',
            'Total chart calculation requests',
            ['chart_type', 'ayanamsa']
        )

        # Advanced Performance Metrics (Phase 2.2)
        self.database_query_duration = Histogram(
            'astro_engine_database_query_duration_seconds',
            'Database query execution time',
            ['query_type'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )

        self.api_response_time_percentiles = Summary(
            'astro_engine_api_response_time_seconds',
            'API response time percentiles',
            ['endpoint', 'status']
        )

        self.concurrent_users_active = Gauge(
            'astro_engine_concurrent_users_active',
            'Current number of active concurrent users'
        )

        self.cache_performance = Summary(
            'astro_engine_cache_performance_seconds',
            'Cache operation performance metrics',
            ['operation_type']
        )

        # Swiss Ephemeris Performance
        self.ephemeris_calculation_time = Histogram(
            'astro_engine_ephemeris_calculation_seconds',
            'Swiss Ephemeris calculation time',
            ['calculation_type'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
        )

        self.ephemeris_file_reads = Counter(
            'astro_engine_ephemeris_file_reads_total',
            'Total Swiss Ephemeris file read operations',
            ['file_name', 'status']
        )

        # Advanced Business Metrics
        self.calculation_complexity = Histogram(
            'astro_engine_calculation_complexity',
            'Calculation complexity score',
            ['chart_type'],
            buckets=[1, 5, 10, 25, 50, 100, 250, 500]
        )

        self.user_interaction_rate = Counter(
            'astro_engine_user_interactions_total',
            'User interaction events',
            ['interaction_type', 'endpoint']
        )

        self.error_rate_percentage = Gauge(
            'astro_engine_error_rate_percentage',
            'Current error rate as percentage'
        )

        self.peak_concurrent_users = Gauge(
            'astro_engine_peak_concurrent_users',
            'Peak concurrent users in current session'
        )

        # Resource Utilization
        self.cpu_usage_percentage = Gauge(
            'astro_engine_cpu_usage_percentage',
            'Current CPU usage percentage'
        )

        self.memory_usage_percentage = Gauge(
            'astro_engine_memory_usage_percentage',
            'Current memory usage percentage'
        )

        # Removed Redis memory gauge:
        # self.redis_memory_usage = Gauge(
        #     'astro_engine_redis_memory_bytes',
        #     'Redis memory usage in bytes'
        # )

    def init_app(self, app):
        """Initialize metrics with Flask app"""
        app.metrics_manager = self

        # Set application info
        self.app_info.info({
            'version': app.config.get('VERSION', '1.3.0'),
            'environment': app.config.get('ENVIRONMENT', 'development'),
            'python_version': os.sys.version,
            'start_time': datetime.utcnow().isoformat()
        })

        # Register request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)

        self.logger.info("🔥 Prometheus metrics manager initialized")

    def _before_request(self):
        """Called before each request"""
        request.start_time = time.time()
        self.active_requests.inc()

    def _after_request(self, response):
        """Called after each request"""
        # Calculate request duration
        duration = time.time() - getattr(request, 'start_time', time.time())

        # Get endpoint info
        endpoint = request.endpoint or 'unknown'
        method = request.method
        status_code = str(response.status_code)

        # Update metrics
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        # Request/Response size
        if hasattr(request, 'content_length') and request.content_length:
            self.request_size.labels(
                method=method,
                endpoint=endpoint
            ).observe(request.content_length)

        if response.content_length:
            self.response_size.labels(
                method=method,
                endpoint=endpoint
            ).observe(response.content_length)

        # Decrement active requests
        self.active_requests.dec()

        return response

    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation metrics"""
        self.cache_operations.labels(
            operation=operation,
            result=result
        ).inc()

    def update_cache_hit_rate(self, hit_rate: float):
        """Update cache hit rate gauge"""
        self.cache_hit_rate.set(hit_rate)

    def record_calculation(self, calc_type: str, duration: float, cached: bool = False):
        """Record calculation metrics"""
        self.calculation_duration.labels(
            calculation_type=calc_type
        ).observe(duration)

        self.calculation_count.labels(
            calculation_type=calc_type,
            cached=str(cached).lower()
        ).inc()

    def record_chart_request(self, chart_type: str, ayanamsa: str = 'lahiri'):
        """Record chart request metrics"""
        self.chart_requests.labels(
            chart_type=chart_type,
            ayanamsa=ayanamsa
        ).inc()

    def record_error(self, error_type: str, endpoint: str = 'unknown'):
        """Record error metrics"""
        self.error_count.labels(
            error_type=error_type,
            endpoint=endpoint
        ).inc()

    def record_ephemeris_access(self, file_type: str = 'se1'):
        """Record Swiss Ephemeris file access"""
        self.ephemeris_access.labels(
            file_type=file_type
        ).inc()

    def update_system_metrics(self):
        """Update system-level metrics"""
        try:
            import psutil
            process = psutil.Process()
            self.memory_usage.set(process.memory_info().rss)
        except ImportError:
            import resource
            self.memory_usage.set(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
        except Exception as e:
            self.logger.error(f"Error updating system metrics: {e}")

    # Removed Redis metric updater:
    # def update_redis_metrics(self, cache_manager):
    #     ...

    # Advanced Metrics Methods (Phase 2.2)

    def record_database_query(self, query_type: str, duration: float):
        """Record database query performance"""
        self.database_query_duration.labels(query_type=query_type).observe(duration)

    def record_api_response_time(self, endpoint: str, status: str, duration: float):
        """Record API response time for percentile tracking"""
        self.api_response_time_percentiles.labels(
            endpoint=endpoint,
            status=status
        ).observe(duration)

    def update_concurrent_users(self, count: int):
        """Update current concurrent users count"""
        self.concurrent_users_active.set(count)

        # Track peak - safely get current peak value
        try:
            current_peak = 0
            if hasattr(self.peak_concurrent_users, '_value'):
                if hasattr(self.peak_concurrent_users._value, '_value'):
                    current_peak = self.peak_concurrent_users._value._value
                else:
                    current_peak = self.peak_concurrent_users._value

            if count > current_peak:
                self.peak_concurrent_users.set(count)
        except Exception as e:
            self.logger.error(f"Error updating peak concurrent users: {e}")
            self.peak_concurrent_users.set(count)

    def record_cache_performance(self, operation_type: str, duration: float):
        """Record cache operation performance"""
        self.cache_performance.labels(operation_type=operation_type).observe(duration)

    def record_ephemeris_calculation(self, calc_type: str, duration: float):
        """Record Swiss Ephemeris calculation time"""
        self.ephemeris_calculation_time.labels(
            calculation_type=calc_type
        ).observe(duration)

    def record_ephemeris_file_read(self, file_name: str, status: str = 'success'):
        """Record Swiss Ephemeris file read operation"""
        self.ephemeris_file_reads.labels(
            file_name=file_name,
            status=status
        ).inc()

    def record_calculation_complexity(self, chart_type: str, complexity_score: int):
        """Record calculation complexity score"""
        self.calculation_complexity.labels(chart_type=chart_type).observe(complexity_score)

    def record_user_interaction(self, interaction_type: str, endpoint: str):
        """Record user interaction events"""
        self.user_interaction_rate.labels(
            interaction_type=interaction_type,
            endpoint=endpoint
        ).inc()

    def update_error_rate(self, percentage: float):
        """Update current error rate percentage"""
        self.error_rate_percentage.set(percentage)

    def update_resource_utilization(self):
        """Update CPU and memory utilization metrics"""
        try:
            import psutil

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage_percentage.set(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage_percentage.set(memory.percent)

            # Process-specific memory
            process = psutil.Process()
            process_memory = process.memory_info().rss
            self.memory_usage.set(process_memory)

        except ImportError:
            import resource
            process_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
            self.memory_usage.set(process_memory)
        except Exception as e:
            self.logger.error(f"Error updating resource utilization: {e}")

    def calculate_and_update_error_rate(self):
        """Calculate and update error rate from request metrics"""
        try:
            total_requests = 0
            error_requests = 0

            for metric in self.request_count.collect():
                for sample in metric.samples:
                    total_requests += sample.value
                    if sample.labels.get('status_code', '').startswith(('4', '5')):
                        error_requests += sample.value

            if total_requests > 0:
                error_rate = (error_requests / total_requests) * 100
                self.update_error_rate(error_rate)

        except Exception as e:
            self.logger.error(f"Error calculating error rate: {e}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            def safe_get_gauge_value(gauge):
                try:
                    if hasattr(gauge, '_value') and hasattr(gauge._value, '_value'):
                        return gauge._value._value
                    elif hasattr(gauge, '_value'):
                        return gauge._value
                    else:
                        return 0.0
                except:
                    return 0.0

            summary = {
                'timestamp': datetime.utcnow().isoformat(),
                'active_requests': safe_get_gauge_value(self.active_requests),
                'concurrent_users': safe_get_gauge_value(self.concurrent_users_active),
                'peak_concurrent_users': safe_get_gauge_value(self.peak_concurrent_users),
                'cache_hit_rate': safe_get_gauge_value(self.cache_hit_rate),
                'error_rate_percentage': safe_get_gauge_value(self.error_rate_percentage),
                'memory_usage_mb': safe_get_gauge_value(self.memory_usage) / (1024 * 1024),
                'cpu_usage_percentage': safe_get_gauge_value(self.cpu_usage_percentage),
                # Removed Redis values:
                # 'redis_connections': safe_get_gauge_value(self.redis_connections),
                # 'redis_memory_mb': safe_get_gauge_value(self.redis_memory_usage) / (1024 * 1024)
            }
            return summary
        except Exception as e:
            self.logger.error(f"Error generating performance summary: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': f"Failed to generate summary: {e}"
            }

    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        try:
            return generate_latest(REGISTRY)
        except Exception as e:
            self.logger.error(f"Error generating metrics: {e}")
            return ""


def metrics_decorator(calculation_type: str):
    """
    Decorator to automatically track calculation metrics

    Usage:
        @metrics_decorator('natal_chart')
        def calculate_natal_chart():
            # calculation logic
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                if hasattr(current_app, 'metrics_manager'):
                    metrics_manager = current_app.metrics_manager

                    cached = False
                    if hasattr(result, 'get_json'):
                        try:
                            json_data = result.get_json()
                            if json_data and isinstance(json_data, dict):
                                perf_data = json_data.get('_performance', {})
                                cached = perf_data.get('cached', False)
                        except:
                            pass
                    elif isinstance(result, dict):
                        perf_data = result.get('_performance', {})
                        cached = perf_data.get('cached', False)

                    metrics_manager.record_calculation(calculation_type, duration, cached)

                return result

            except Exception as e:
                duration = time.time() - start_time

                if hasattr(current_app, 'metrics_manager'):
                    endpoint = getattr(request, 'endpoint', 'unknown')
                    current_app.metrics_manager.record_error(
                        error_type=type(e).__name__,
                        endpoint=endpoint
                    )

                raise e

        return wrapper
    return decorator


def create_metrics_manager(app):
    """Factory function to create and configure metrics manager"""
    if hasattr(app, 'metrics_manager'):
        return app.metrics_manager

    metrics_manager = AstroMetricsManager(app)
    return metrics_manager
