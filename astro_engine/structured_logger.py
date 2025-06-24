# Structured Logging Manager for Astro Engine
# Phase 3.1: Logging Framework Implementation

import structlog
import logging
import logging.handlers
import sys
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g, current_app
from functools import wraps
import traceback

class AstroStructuredLogger:
    """
    Centralized structured logging for Astro Engine
    Implements JSON-based structured logging with correlation IDs and context
    
    Phase 3.3 Features:
    - Log rotation with configurable size and backup count
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Separate log files for different log levels
    - Log aggregation support with structured JSON output
    - Production-ready logging configuration
    """
    
    def __init__(self, app=None):
        self.logger = None
        self.correlation_id_header = 'X-Correlation-ID'
        self.log_dir = None
        self.handlers = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize structured logging with Flask app"""
        app.structured_logger = self
        
        # Set up log directory
        self.log_dir = os.getenv('LOG_DIR', os.path.join(os.getcwd(), 'logs'))
        self._ensure_log_directory()
        
        # Configure structlog
        self._configure_structlog()
        
        # Set up file handlers with rotation
        self._setup_log_rotation()
        
        # Set up application logger
        self.logger = structlog.get_logger("astro_engine")
        
        # Register Flask hooks for request tracking
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Global error handler
        app.teardown_appcontext(self._teardown_request)
        
        self.logger.info("🔥 Structured logging manager initialized", 
                        component="logging_manager",
                        log_level="INFO",
                        log_dir=self.log_dir,
                        rotation_enabled=True)
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"📁 Created log directory: {self.log_dir}")
    
    def _setup_log_rotation(self):
        """Set up rotating file handlers for different log levels"""
        
        # Configuration for log rotation
        max_bytes = int(os.getenv('LOG_MAX_BYTES', 50 * 1024 * 1024))  # 50MB default
        backup_count = int(os.getenv('LOG_BACKUP_COUNT', 5))  # 5 backups default
        
        # Main application log (all levels)
        app_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, 'astro_engine.log'),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        app_handler.setLevel(logging.DEBUG)
        app_formatter = logging.Formatter('%(message)s')
        app_handler.setFormatter(app_formatter)
        
        # Error log (WARNING and above)
        error_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, 'astro_engine_errors.log'),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(app_formatter)
        
        # Performance log (specific for performance metrics)
        perf_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, 'astro_engine_performance.log'),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(app_formatter)
        
        # Add handlers to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(app_handler)
        root_logger.addHandler(error_handler)
        
        # Store handlers for management
        self.handlers = {
            'app': app_handler,
            'error': error_handler,
            'performance': perf_handler
        }
        
        print(f"📋 Log rotation configured:")
        print(f"   📄 Main log: astro_engine.log ({max_bytes//1024//1024}MB, {backup_count} backups)")
        print(f"   🚨 Error log: astro_engine_errors.log ({max_bytes//1024//1024}MB, {backup_count} backups)")
        print(f"   ⚡ Performance log: astro_engine_performance.log ({max_bytes//1024//1024}MB, {backup_count} backups)")
    
    def get_log_configuration(self):
        """Get current logging configuration for status endpoint"""
        return {
            "structured_logging": True,
            "log_level": logging.getLevelName(logging.getLogger().level),
            "log_directory": self.log_dir,
            "rotation_enabled": True,
            "max_log_size_mb": int(os.getenv('LOG_MAX_BYTES', 50 * 1024 * 1024)) // 1024 // 1024,
            "backup_count": int(os.getenv('LOG_BACKUP_COUNT', 5)),
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "correlation_id_header": self.correlation_id_header,
            "log_files": {
                "main": "astro_engine.log",
                "errors": "astro_engine_errors.log", 
                "performance": "astro_engine_performance.log"
            },
            "handlers_active": len(self.handlers),
            "json_output": os.getenv('ENVIRONMENT', 'development') == 'production'
        }

    def _configure_structlog(self):
        """Configure structlog with processors and renderers"""
        
        # Define processors
        processors = [
            # Add correlation ID to all logs
            self._add_correlation_id,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Add log level
            structlog.stdlib.add_log_level,
            # Add logger name
            structlog.stdlib.add_logger_name,
            # Add call site info for errors
            structlog.processors.CallsiteParameterAdder(
                parameters=[structlog.processors.CallsiteParameter.FILENAME,
                           structlog.processors.CallsiteParameter.FUNC_NAME,
                           structlog.processors.CallsiteParameter.LINENO]
            ),
            # Stack info for exceptions
            structlog.processors.StackInfoRenderer(),
            # Format exceptions nicely
            structlog.processors.format_exc_info,
        ]
        
        # Add JSON renderer for production
        if os.getenv('ENVIRONMENT', 'development') == 'production':
            processors.append(structlog.processors.JSONRenderer())
        else:
            # Pretty console output for development
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        
        # Configure structlog
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure stdlib logging
        log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
        logging.basicConfig(
            format="%(message)s",
            level=log_level,
            stream=sys.stdout,
        )
    
    def _add_correlation_id(self, logger, method_name, event_dict):
        """Add correlation ID to log entries"""
        try:
            from flask import g
            correlation_id = getattr(g, 'correlation_id', None)
            if correlation_id:
                event_dict['correlation_id'] = correlation_id
        except RuntimeError:
            # Working outside of application context, skip correlation ID
            pass
        return event_dict
    
    def _before_request(self):
        """Set up request context for logging"""
        # Generate or extract correlation ID
        correlation_id = request.headers.get(self.correlation_id_header)
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        g.correlation_id = correlation_id
        g.request_start_time = datetime.utcnow()
        
        # Log request start
        self.logger.info("Request started",
                        method=request.method,
                        path=request.path,
                        remote_addr=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', 'unknown'),
                        content_type=request.headers.get('Content-Type', 'unknown'),
                        content_length=request.headers.get('Content-Length', 0))
    
    def _after_request(self, response):
        """Log request completion"""
        duration = None
        if hasattr(g, 'request_start_time'):
            duration = (datetime.utcnow() - g.request_start_time).total_seconds()
        
        self.logger.info("Request completed",
                        status_code=response.status_code,
                        duration_seconds=duration,
                        response_size=response.headers.get('Content-Length', 0))
        
        # Add correlation ID to response headers
        if hasattr(g, 'correlation_id'):
            response.headers[self.correlation_id_header] = g.correlation_id
        
        return response
    
    def _teardown_request(self, exception=None):
        """Clean up request context"""
        if exception:
            self.logger.error("Request failed with exception",
                            exception_type=type(exception).__name__,
                            exception_message=str(exception),
                            traceback=traceback.format_exc())
    
    def get_logger(self, component: str) -> structlog.BoundLogger:
        """Get a component-specific logger"""
        return self.logger.bind(component=component)
    
    def log_calculation_start(self, calculation_type: str, input_data: Dict[str, Any]):
        """Log calculation start with input parameters"""
        # Sanitize sensitive data
        safe_data = {k: v for k, v in input_data.items() 
                    if k not in ['password', 'token', 'secret']}
        
        self.logger.info("Calculation started",
                        calculation_type=calculation_type,
                        input_parameters=safe_data,
                        component="calculation_engine")
    
    def log_calculation_complete(self, calculation_type: str, duration: float, 
                               cached: bool = False, result_size: int = 0):
        """Log calculation completion with performance data"""
        self.logger.info("Calculation completed",
                        calculation_type=calculation_type,
                        duration_seconds=duration,
                        cached=cached,
                        result_size_bytes=result_size,
                        component="calculation_engine")
    
    def log_cache_operation(self, operation: str, key: str, result: str, 
                          duration: float = 0):
        """Log cache operations"""
        self.logger.debug("Cache operation",
                         operation=operation,
                         cache_key=key,
                         result=result,
                         duration_seconds=duration,
                         component="cache_manager")
    
    def log_error(self, error_type: str, message: str, context: Dict[str, Any] = None,
                 exception: Exception = None):
        """Log errors with context"""
        log_data = {
            "error_type": error_type,
            "error_message": message,
            "component": "error_handler"
        }
        
        if context:
            log_data.update(context)
        
        if exception:
            log_data["exception_traceback"] = traceback.format_exc()
        
        self.logger.error("Application error", **log_data)
    
    def log_performance_metric(self, metric_name: str, value: float, 
                             unit: str = "seconds", context: Dict[str, Any] = None):
        """Log performance metrics"""
        log_data = {
            "metric_name": metric_name,
            "metric_value": value,
            "metric_unit": unit,
            "component": "performance_monitor"
        }
        
        if context:
            log_data.update(context)
        
        self.logger.info("Performance metric", **log_data)
    
    def log_business_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log business events for analytics"""
        self.logger.info("Business event",
                        event_type=event_type,
                        event_data=event_data,
                        component="business_analytics")
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        self.logger.warning("Security event",
                           event_type=event_type,
                           details=details,
                           component="security_monitor")


def structured_log_decorator(calculation_type: str, log_inputs: bool = True):
    """
    Decorator to automatically log calculation operations
    
    Usage:
        @structured_log_decorator('natal_chart')
        def calculate_natal_chart(data):
            # calculation logic
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(current_app, 'structured_logger'):
                # Fallback if structured logger not available
                return func(*args, **kwargs)
            
            logger = current_app.structured_logger
            start_time = datetime.utcnow()
            
            # Log inputs if requested
            if log_inputs and len(args) > 0:
                # Assume first argument contains input data
                input_data = args[0] if isinstance(args[0], dict) else {}
                logger.log_calculation_start(calculation_type, input_data)
            else:
                logger.get_logger("calculation").info(
                    "Calculation started",
                    calculation_type=calculation_type
                )
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                # Determine if result was cached
                cached = False
                result_size = 0
                
                if isinstance(result, dict) and '_performance' in result:
                    cached = result['_performance'].get('cached', False)
                    result_size = len(str(result)) if result else 0
                
                logger.log_calculation_complete(
                    calculation_type, 
                    duration, 
                    cached, 
                    result_size
                )
                
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.log_error(
                    error_type=type(e).__name__,
                    message=str(e),
                    context={
                        'calculation_type': calculation_type,
                        'duration_seconds': duration
                    },
                    exception=e
                )
                raise
        
        return wrapper
    return decorator


def create_structured_logger(app):
    """Factory function to create and configure structured logger"""
    structured_logger = AstroStructuredLogger(app)
    return structured_logger
