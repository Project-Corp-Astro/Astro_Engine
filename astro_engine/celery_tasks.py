# Celery Tasks for Astrological Calculations
# Phase 4.2: Async Tasks Implementation

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import structlog

# Add project path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Celery imports
from celery import Celery
from celery.exceptions import Retry

# Create Celery app instance
celery_app = Celery('astro_engine')

# Configure Celery
celery_app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Set up logger
logger = structlog.get_logger("celery_tasks")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def calculate_natal_chart_async(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async task for natal chart calculation
    
    Args:
        birth_data: Dictionary containing name, date, time, lat, lng, timezone
    
    Returns:
        Natal chart calculation result
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info("🔄 Starting natal chart calculation",
               task_id=task_id,
               birth_data=birth_data)
    
    try:
        # Import calculation modules (lazy import to avoid circular dependencies)
        from astro_engine.engine.routes.LahairiAyanmasa import calculate_natal_chart_data
        
        # Validate input data
        required_fields = ['name', 'date', 'time', 'latitude', 'longitude', 'timezone']
        for field in required_fields:
            if field not in birth_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Perform calculation
        result = calculate_natal_chart_data(
            name=birth_data['name'],
            date=birth_data['date'],
            time=birth_data['time'],
            latitude=birth_data['latitude'],
            longitude=birth_data['longitude'],
            timezone=birth_data['timezone']
        )
        
        duration = time.time() - start_time
        
        logger.info("✅ Natal chart calculation completed",
                   task_id=task_id,
                   duration=duration,
                   result_size=len(str(result)))
        
        return {
            'success': True,
            'result': result,
            'task_id': task_id,
            'calculation_type': 'natal_chart',
            'duration': duration,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Natal chart calculation failed",
                    task_id=task_id,
                    error=str(e),
                    birth_data=birth_data)
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info("🔄 Retrying natal chart calculation",
                       task_id=task_id,
                       retry_count=self.request.retries + 1)
            raise self.retry(countdown=60, exc=e)
        
        return {
            'success': False,
            'error': str(e),
            'task_id': task_id,
            'calculation_type': 'natal_chart',
            'failed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def calculate_divisional_chart_async(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async task for divisional chart calculation
    
    Args:
        chart_data: Dictionary containing chart parameters and division type
    
    Returns:
        Divisional chart calculation result
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info("🔄 Starting divisional chart calculation",
               task_id=task_id,
               chart_type=chart_data.get('division_type'),
               chart_data=chart_data)
    
    try:
        # Import calculation modules
        from astro_engine.engine.routes.LahairiAyanmasa import calculate_divisional_chart_data
        
        # Validate input data
        required_fields = ['name', 'date', 'time', 'latitude', 'longitude', 'timezone', 'division_type']
        for field in required_fields:
            if field not in chart_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Perform calculation based on division type
        division_type = chart_data['division_type']
        
        result = calculate_divisional_chart_data(
            name=chart_data['name'],
            date=chart_data['date'],
            time=chart_data['time'],
            latitude=chart_data['latitude'],
            longitude=chart_data['longitude'],
            timezone=chart_data['timezone'],
            division=division_type
        )
        
        duration = time.time() - start_time
        
        logger.info("✅ Divisional chart calculation completed",
                   task_id=task_id,
                   division_type=division_type,
                   duration=duration,
                   result_size=len(str(result)))
        
        return {
            'success': True,
            'result': result,
            'task_id': task_id,
            'calculation_type': f'divisional_chart_{division_type}',
            'division_type': division_type,
            'duration': duration,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Divisional chart calculation failed",
                    task_id=task_id,
                    division_type=chart_data.get('division_type'),
                    error=str(e),
                    chart_data=chart_data)
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info("🔄 Retrying divisional chart calculation",
                       task_id=task_id,
                       retry_count=self.request.retries + 1)
            raise self.retry(countdown=60, exc=e)
        
        return {
            'success': False,
            'error': str(e),
            'task_id': task_id,
            'calculation_type': f'divisional_chart_{chart_data.get("division_type")}',
            'failed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def calculate_bulk_charts_async(self, bulk_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async task for bulk chart calculations
    
    Args:
        bulk_request: Dictionary containing multiple chart requests
    
    Returns:
        Bulk calculation results
    """
    task_id = self.request.id
    start_time = time.time()
    
    charts = bulk_request.get('charts', [])
    
    logger.info("🔄 Starting bulk chart calculation",
               task_id=task_id,
               chart_count=len(charts))
    
    try:
        results = []
        errors = []
        
        for i, chart_data in enumerate(charts):
            try:
                chart_type = chart_data.get('type', 'natal')
                
                if chart_type == 'natal':
                    # Call natal chart calculation function directly
                    from astro_engine.engine.routes.LahairiAyanmasa import calculate_natal_chart_data
                    
                    result = calculate_natal_chart_data(
                        name=chart_data['name'],
                        date=chart_data['date'],
                        time=chart_data['time'],
                        latitude=chart_data['latitude'],
                        longitude=chart_data['longitude'],
                        timezone=chart_data['timezone']
                    )
                    
                    results.append({
                        'index': i,
                        'chart_type': chart_type,
                        'success': True,
                        'result': result,
                        'name': chart_data['name']
                    })
                    
                elif chart_type.startswith('divisional_'):
                    # Divisional chart calculation
                    from astro_engine.engine.routes.LahairiAyanmasa import calculate_divisional_chart_data
                    
                    division_type = chart_data.get('division_type', 'D9')
                    
                    result = calculate_divisional_chart_data(
                        name=chart_data['name'],
                        date=chart_data['date'],
                        time=chart_data['time'],
                        latitude=chart_data['latitude'],
                        longitude=chart_data['longitude'],
                        timezone=chart_data['timezone'],
                        division=division_type
                    )
                    
                    results.append({
                        'index': i,
                        'chart_type': f'{chart_type}_{division_type}',
                        'success': True,
                        'result': result,
                        'name': chart_data['name']
                    })
                
                else:
                    raise ValueError(f"Unsupported chart type: {chart_type}")
                
            except Exception as chart_error:
                logger.error("❌ Individual chart calculation failed",
                           task_id=task_id,
                           chart_index=i,
                           error=str(chart_error))
                
                errors.append({
                    'index': i,
                    'error': str(chart_error),
                    'name': chart_data.get('name', 'Unknown')
                })
        
        duration = time.time() - start_time
        success_count = len(results)
        error_count = len(errors)
        
        logger.info("✅ Bulk chart calculation completed",
                   task_id=task_id,
                   duration=duration,
                   success_count=success_count,
                   error_count=error_count)
        
        return {
            'success': True,
            'task_id': task_id,
            'calculation_type': 'bulk_charts',
            'total_charts': len(charts),
            'successful_charts': success_count,
            'failed_charts': error_count,
            'results': results,
            'errors': errors,
            'duration': duration,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Bulk chart calculation failed",
                    task_id=task_id,
                    error=str(e))
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info("🔄 Retrying bulk chart calculation",
                       task_id=task_id,
                       retry_count=self.request.retries + 1)
            raise self.retry(countdown=60, exc=e)
        
        return {
            'success': False,
            'error': str(e),
            'task_id': task_id,
            'calculation_type': 'bulk_charts',
            'failed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def test_task_async(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple test task for validating Celery functionality
    
    Args:
        test_data: Test data to process
    
    Returns:
        Test result
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info("🧪 Starting test task",
               task_id=task_id,
               test_data=test_data)
    
    try:
        # Simulate some work
        import time
        work_duration = test_data.get('work_duration', 2)
        time.sleep(work_duration)
        
        duration = time.time() - start_time
        
        result = {
            'message': 'Test task completed successfully',
            'input_data': test_data,
            'processed_at': datetime.utcnow().isoformat(),
            'work_duration': work_duration,
            'actual_duration': duration
        }
        
        logger.info("✅ Test task completed",
                   task_id=task_id,
                   duration=duration)
        
        return {
            'success': True,
            'result': result,
            'task_id': task_id,
            'calculation_type': 'test_task',
            'duration': duration,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Test task failed",
                    task_id=task_id,
                    error=str(e))
        
        return {
            'success': False,
            'error': str(e),
            'task_id': task_id,
            'calculation_type': 'test_task',
            'failed_at': datetime.utcnow().isoformat()
        }

# Task registry for easy access
AVAILABLE_TASKS = {
    'natal_chart': calculate_natal_chart_async,
    'divisional_chart': calculate_divisional_chart_async,
    'bulk_charts': calculate_bulk_charts_async,
    'test_task': test_task_async
}

def get_available_tasks() -> List[str]:
    """Get list of available task names"""
    return list(AVAILABLE_TASKS.keys())

if __name__ == '__main__':
    # Start Celery worker if run directly
    celery_app.start()
