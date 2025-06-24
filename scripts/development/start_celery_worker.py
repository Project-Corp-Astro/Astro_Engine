#!/usr/bin/env python3
"""
Celery Worker Startup Script for Astro Engine
Starts the Celery worker process to handle async tasks
"""

import os
import sys
from astro_engine.celery_tasks import celery_app

if __name__ == '__main__':
    # Set environment variables
    os.environ.setdefault('PYTHONPATH', os.path.dirname(os.path.abspath(__file__)))
    
    # Start Celery worker
    print("🚀 Starting Astro Engine Celery Worker...")
    print(f"📊 Broker: {celery_app.conf.broker_url}")
    print(f"💾 Backend: {celery_app.conf.result_backend}")
    print("⚡ Available queues: astro_calculations")
    print("=" * 60)
    
    # Start worker with configuration
    celery_app.start([
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--queues=astro_calculations',
        '--hostname=astro_worker@%h',
        '--pool=solo' if os.name == 'nt' else 'prefork'
    ])
