# Celery Task Queue Manager for Astro Engine
# Phase 4.1: Celery Setup and Framework

import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from celery import Celery
from celery.result import AsyncResult
import structlog
import redis
import json
import traceback

class AstroCeleryManager:
    """
    Centralized Celery task queue manager for Astro Engine
    Implements async task processing, monitoring, and result management
    
    Phase 4.1 Features:
    - Celery worker configuration with Redis broker
    - Task framework for astrological calculations
    - Result storage and retrieval
    - Task status tracking and monitoring
    - Error handling and retry logic
    """
    
    def __init__(self, app=None):
        self.celery_app = None
        self.redis_client = None
        self.logger = structlog.get_logger("celery_manager")
        self.task_results = {}  # In-memory cache for recent results
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Celery with Flask app"""
        
        # Configuration
        broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
        result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
        
        # Create Celery instance
        self.celery_app = Celery(
            'astro_engine',
            broker=broker_url,
            backend=result_backend,
            include=['astro_engine.celery_tasks']
        )
        
        # Configure Celery
        self.celery_app.conf.update(
            # Task settings
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            
            # Result settings
            result_expires=3600,  # 1 hour
            result_cache_max=100,
            
            # Worker settings
            worker_pool='solo' if os.name == 'nt' else 'prefork',
            worker_concurrency=2,
            worker_prefetch_multiplier=1,
            
            # Task routing
            task_routes={
                'astro_engine.celery_tasks.*': {'queue': 'astro_calculations'},
            },
            
            # Retry settings
            task_acks_late=True,
            task_reject_on_worker_lost=True,
            task_default_retry_delay=60,
            task_max_retries=3,
            
            # Monitoring
            worker_send_task_events=True,
            task_send_sent_event=True,
        )
        
        # Set up Redis client for additional operations
        try:
            self.redis_client = redis.from_url(broker_url)
            self.redis_client.ping()
            self.logger.info("✅ Redis connected for Celery operations")
        except Exception as e:
            self.logger.error("❌ Redis connection failed", error=str(e))
            self.redis_client = None
        
        # Store in Flask app
        app.celery_manager = self
        
        self.logger.info("🔥 Celery task manager initialized",
                        broker=broker_url,
                        backend=result_backend,
                        worker_pool=self.celery_app.conf.worker_pool)
    
    def get_celery_app(self):
        """Get the Celery application instance"""
        return self.celery_app
    
    def submit_task(self, task_name: str, task_args: List = None, task_kwargs: Dict = None, 
                   priority: int = 5, eta: datetime = None) -> Dict[str, Any]:
        """
        Submit a task to the Celery queue
        
        Args:
            task_name: Name of the task function
            task_args: Positional arguments for the task
            task_kwargs: Keyword arguments for the task
            priority: Task priority (0-9, higher is more priority)
            eta: Estimated time of arrival (when to execute)
        
        Returns:
            Task submission result with task_id and status
        """
        if not self.celery_app:
            return {'error': 'Celery not initialized', 'success': False}
        
        task_args = task_args or []
        task_kwargs = task_kwargs or {}
        
        try:
            # Submit task
            result = self.celery_app.send_task(
                task_name,
                args=task_args,
                kwargs=task_kwargs,
                priority=priority,
                eta=eta,
                queue='astro_calculations'
            )
            
            # Store task info
            task_info = {
                'task_id': result.id,
                'task_name': task_name,
                'submitted_at': datetime.utcnow().isoformat(),
                'status': 'PENDING',
                'priority': priority,
                'eta': eta.isoformat() if eta else None,
                'args': task_args,
                'kwargs': task_kwargs
            }
            
            self.task_results[result.id] = task_info
            
            self.logger.info("📤 Task submitted to queue",
                           task_id=result.id,
                           task_name=task_name,
                           priority=priority)
            
            return {
                'success': True,
                'task_id': result.id,
                'status': 'PENDING',
                'submitted_at': task_info['submitted_at']
            }
            
        except Exception as e:
            self.logger.error("❌ Failed to submit task",
                            task_name=task_name,
                            error=str(e),
                            traceback=traceback.format_exc())
            
            return {
                'success': False,
                'error': str(e),
                'task_name': task_name
            }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status and result of a task"""
        if not self.celery_app:
            return {'error': 'Celery not initialized', 'success': False}
        
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            
            task_info = {
                'task_id': task_id,
                'status': result.status,
                'ready': result.ready(),
                'successful': result.successful() if result.ready() else None,
                'failed': result.failed() if result.ready() else None,
            }
            
            # Add result if available
            if result.ready():
                if result.successful():
                    task_info['result'] = result.result
                    task_info['completed_at'] = datetime.utcnow().isoformat()
                elif result.failed():
                    task_info['error'] = str(result.result)
                    task_info['traceback'] = result.traceback
                    task_info['failed_at'] = datetime.utcnow().isoformat()
            
            # Add stored task info if available
            if task_id in self.task_results:
                stored_info = self.task_results[task_id]
                task_info.update({
                    'task_name': stored_info.get('task_name'),
                    'submitted_at': stored_info.get('submitted_at'),
                    'priority': stored_info.get('priority'),
                    'args': stored_info.get('args'),
                    'kwargs': stored_info.get('kwargs')
                })
            
            return {
                'success': True,
                'task_info': task_info
            }
            
        except Exception as e:
            self.logger.error("❌ Failed to get task status",
                            task_id=task_id,
                            error=str(e))
            
            return {
                'success': False,
                'error': str(e),
                'task_id': task_id
            }
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a pending or running task"""
        if not self.celery_app:
            return {'error': 'Celery not initialized', 'success': False}
        
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            result.revoke(terminate=True)
            
            self.logger.info("🛑 Task cancelled",
                           task_id=task_id)
            
            return {
                'success': True,
                'task_id': task_id,
                'message': 'Task cancelled successfully'
            }
            
        except Exception as e:
            self.logger.error("❌ Failed to cancel task",
                            task_id=task_id,
                            error=str(e))
            
            return {
                'success': False,
                'error': str(e),
                'task_id': task_id
            }
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics and monitoring info"""
        if not self.celery_app or not self.redis_client:
            return {'error': 'Celery or Redis not available', 'success': False}
        
        try:
            # Get basic queue info
            inspect = self.celery_app.control.inspect()
            
            # Active tasks
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()
            reserved_tasks = inspect.reserved()
            
            # Redis queue length
            try:
                queue_length = self.redis_client.llen('astro_calculations')
            except:
                queue_length = 0
            
            # Recent task results
            recent_tasks = list(self.task_results.values())[-10:]  # Last 10 tasks
            
            stats = {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'queue_stats': {
                    'queue_length': queue_length,
                    'active_tasks': len(active_tasks.get('celery@localhost', [])) if active_tasks else 0,
                    'scheduled_tasks': len(scheduled_tasks.get('celery@localhost', [])) if scheduled_tasks else 0,
                    'reserved_tasks': len(reserved_tasks.get('celery@localhost', [])) if reserved_tasks else 0,
                },
                'recent_tasks': recent_tasks,
                'celery_config': {
                    'broker': self.celery_app.conf.broker_url,
                    'backend': self.celery_app.conf.result_backend,
                    'worker_pool': self.celery_app.conf.worker_pool,
                    'worker_concurrency': self.celery_app.conf.worker_concurrency,
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error("❌ Failed to get queue stats",
                            error=str(e))
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Clean up completed task results older than specified hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            # Clean up local cache
            for task_id in list(self.task_results.keys()):
                task_info = self.task_results[task_id]
                submitted_at = datetime.fromisoformat(task_info['submitted_at'])
                
                if submitted_at < cutoff_time:
                    del self.task_results[task_id]
                    cleaned_count += 1
            
            self.logger.info("🧹 Cleaned up completed tasks",
                           cleaned_count=cleaned_count,
                           max_age_hours=max_age_hours)
            
            return {
                'success': True,
                'cleaned_count': cleaned_count,
                'cutoff_time': cutoff_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error("❌ Failed to cleanup tasks",
                            error=str(e))
            
            return {
                'success': False,
                'error': str(e)
            }

def create_celery_manager(app):
    """Factory function to create and configure Celery manager"""
    return AstroCeleryManager(app)
