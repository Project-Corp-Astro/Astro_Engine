

# from flask import Flask
# from flask_cors import CORS
# import swisseph as swe
# import logging
# from .engine.routes.LahairiAyanmasa import bp
# from .engine.routes.KpNew import kp
# from .engine.routes.RamanAyanmasa import rl
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# logging.basicConfig(level=logging.DEBUG)

# # Set Swiss Ephemeris path
# swe.set_ephe_path('astro_engine/ephe')

# # Register the blueprint containing all routes
# app.register_blueprint(bp)   # lahairi
# app.register_blueprint(kp)      # KP System
# app.register_blueprint(rl)          # Raman  




# if __name__ == "__main__":
#     app.run(debug=True, port=5002)



# from flask import Flask
# from flask_cors import CORS
# import swisseph as swe
# import logging
# from .engine.routes.LahairiAyanmasa import bp
# from .engine.routes.KpNew import kp
# from .engine.routes.RamanAyanmasa import rl
# import sys
# import platform

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# logging.basicConfig(level=logging.DEBUG)

# # Set Swiss Ephemeris path
# swe.set_ephe_path('astro_engine/ephe')

# # Register the blueprint containing all routes
# app.register_blueprint(bp)   # Lahairi Ayanmasa
# app.register_blueprint(kp)      # KP System
# app.register_blueprint(rl)      # Raman Ayanmasa

# if __name__ == "__main__":
#     if len(sys.argv) > 1 and sys.argv[1] == "--production":
#         if platform.system() == 'Windows':
#             # Import and use Waitress on Windows
#             try:
#                 from waitress import serve
#             except ImportError:
#                 print("Waitress is not installed. Please install it with 'pip install waitress'.")
#                 sys.exit(1)
#             serve(app, host='0.0.0.0', port=5002)
#         else:
#             # Import and use Gunicorn on Unix-like systems
#             try:
#                 from gunicorn.app.base import BaseApplication
#             except ImportError:
#                 print("Gunicorn is not installed. Please install it with 'pip install gunicorn'.")
#                 sys.exit(1)

#             class StandaloneApplication(BaseApplication):
#                 def __init__(self, app, options=None):
#                     self.options = options or {}
#                     self.application = app
#                     super().__init__()

#                 def load_config(self):
#                     for key, value in self.options.items():
#                         if key in self.cfg.settings and value is not None:
#                             self.cfg.set(key, value)

#                 def load(self):
#                     return self.application

#             options = {
#                 'bind': '0.0.0.0:5002',
#                 'workers': 4,
#             }
#             StandaloneApplication(app, options).run()
#     else:
#         # Development mode with Flask's built-in server
#         app.run(debug=True, port=5002)




import os
import platform
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import swisseph as swe
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Import blueprints
from .engine.routes.KpNew import kp
from .engine.routes.LahairiAyanmasa import bp
from .engine.routes.RamanAyanmasa import rl

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    # CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    if cors_origins != '*':
        cors_origins = cors_origins.split(',')
    CORS(app, resources={r"/*": {"origins": cors_origins}})
    
    # Rate limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[f"{os.getenv('RATE_LIMIT_REQUESTS', '1000')} per hour"]
    )
    
    # Logging configuration
    log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.getenv('LOG_FILE', 'astro_engine.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set Swiss Ephemeris path
    ephe_path = os.getenv('EPHEMERIS_PATH', 'astro_engine/ephe')
    swe.set_ephe_path(ephe_path)
    
    # Register blueprints
    app.register_blueprint(kp)  # KP System routes
    app.register_blueprint(bp)  # Lahiri Ayanamsa routes
    app.register_blueprint(rl)  # Raman Ayanamsa routes
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers"""
        try:
            # Test Swiss Ephemeris
            jd = swe.julday(2024, 1, 1)
            swe.calc_ut(jd, swe.SUN)
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.3.0',
                'services': {
                    'swiss_ephemeris': 'ok',
                    'api_endpoints': 'ok'
                }
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 503
    
    # Metrics endpoint (basic)
    @app.route('/metrics')
    def metrics():
        """Basic metrics endpoint"""
        if not os.getenv('METRICS_ENABLED', 'true').lower() == 'true':
            return jsonify({'error': 'Metrics disabled'}), 404
            
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'app_name': 'astro_engine',
            'version': '1.3.0',
            'status': 'running'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested endpoint does not exist',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests, please try again later',
            'status_code': 429
        }), 429
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--production":
        if platform.system() == 'Windows':
            # Use Waitress on Windows
            try:
                from waitress import serve
            except ImportError:
                print("Waitress is not installed. Please install it with 'pip install waitress'.")
                sys.exit(1)
            serve(app, host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
        else:
            # Use Gunicorn on Unix-like systems
            try:
                from gunicorn.app.base import BaseApplication
            except ImportError:
                print("Gunicorn is not installed. Please install it with 'pip install gunicorn'.")
                sys.exit(1)

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
                'timeout': int(os.getenv('TIMEOUT', '120'))
            }
            StandaloneApplication(app, options).run()
    else:
        # Development mode
        app.run(
            debug=True, 
            host=os.getenv('HOST', '127.0.0.1'),
            port=int(os.getenv('PORT', '5000'))
        )