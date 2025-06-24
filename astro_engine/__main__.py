#!/usr/bin/env python3
"""
Astro Engine - Main entry point for running as a module

This file allows the astro_engine package to be executed as:
    python -m astro_engine

It provides the main entry point for both development and production deployments.
"""

import os
import sys

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def main():
    """Main entry point for the Astro Engine application."""
    try:
        from astro_engine.app import create_app
        app = create_app()
        
        # Check if we're in production mode
        is_production = os.getenv('FLASK_ENV', '').lower() == 'production'
        
        if is_production:
            # Production mode - use Gunicorn
            import platform
            
            if platform.system() == 'Windows':
                # Use Waitress on Windows
                try:
                    from waitress import serve
                    print("🚀 Starting Astro Engine with Waitress (Production)")
                    serve(app, host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
                except ImportError:
                    print("❌ Waitress is not installed. Please install it with 'pip install waitress'.")
                    sys.exit(1)
            else:
                # Use Gunicorn on Unix-like systems
                try:
                    from gunicorn.app.base import BaseApplication
                    
                    class StandaloneApplication(BaseApplication):
                        def __init__(self, app, options=None):
                            self.options = options or {}
                            self.application = app
                            super().__init__()

                        def load_config(self):
                            for key, value in self.options.items():
                                if key in self.cfg.settings and value is not None:
                                    self.cfg.set(key, value)

                        def load(self):
                            return self.application

                    options = {
                        'bind': f"0.0.0.0:{os.getenv('PORT', '5000')}",
                        'workers': int(os.getenv('WORKERS', '2')),
                        'worker_class': 'gthread',
                        'threads': 4,
                        'timeout': int(os.getenv('TIMEOUT', '120')),
                        'preload_app': True,
                        'max_requests': 1000,
                        'max_requests_jitter': 100
                    }
                    
                    print("🚀 Starting Astro Engine with Gunicorn (Production)")
                    StandaloneApplication(app, options).run()
                    
                except ImportError:
                    print("❌ Gunicorn is not installed. Please install it with 'pip install gunicorn'.")
                    sys.exit(1)
        else:
            # Development mode - use Flask's built-in server
            print("🔧 Starting Astro Engine in Development Mode")
            print("⚠️  This is NOT suitable for production use!")
            app.run(
                debug=True, 
                host=os.getenv('HOST', '127.0.0.1'),
                port=int(os.getenv('PORT', '5000'))
            )
            
    except Exception as e:
        print(f"❌ Failed to start Astro Engine: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
