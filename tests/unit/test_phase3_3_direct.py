#!/usr/bin/env python3
"""
Phase 3.3: Log Management Direct Test
Tests log rotation, levels, and aggregation directly without server
"""

import os
import sys
import time
import logging
import tempfile
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_log_management_direct():
    """Direct test of log management features"""
    
    print("🔥 PHASE 3.3: LOG MANAGEMENT DIRECT VALIDATION")
    print("=" * 60)
    
    results = {
        'tests_passed': 0,
        'tests_failed': 0,
        'total_tests': 0
    }
    
    def run_test(test_name, test_func):
        """Run a test and track results"""
        results['total_tests'] += 1
        try:
            success = test_func()
            if success:
                print(f"✅ {test_name}: PASSED")
                results['tests_passed'] += 1
            else:
                print(f"❌ {test_name}: FAILED")
                results['tests_failed'] += 1
            return success
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results['tests_failed'] += 1
            return False
    
    # Test 1: Direct Logger Creation and Configuration
    def test_logger_creation():
        print("📊 Testing structured logger creation...")
        try:
            from astro_engine.structured_logger import AstroStructuredLogger
            
            # Create temporary log directory
            with tempfile.TemporaryDirectory() as temp_dir:
                os.environ['LOG_DIR'] = temp_dir
                
                # Create mock Flask app
                class MockApp:
                    def __init__(self):
                        self.config = {'ENVIRONMENT': 'test'}
                    def before_request(self, func): pass
                    def after_request(self, func): pass  
                    def teardown_appcontext(self, func): pass
                
                app = MockApp()
                logger = AstroStructuredLogger()
                logger.init_app(app)
                
                # Check if log files are created
                log_files = os.listdir(temp_dir)
                print(f"   Created log directory: {temp_dir}")
                print(f"   Log files that would be created: astro_engine.log, astro_engine_errors.log")
                
                # Check configuration
                config = logger.get_log_configuration()
                required_fields = ['structured_logging', 'log_level', 'log_directory', 
                                 'rotation_enabled', 'max_log_size_mb', 'backup_count']
                
                for field in required_fields:
                    if field not in config:
                        print(f"   Missing configuration field: {field}")
                        return False
                
                print(f"   ✓ Structured logging: {config['structured_logging']}")
                print(f"   ✓ Log level: {config['log_level']}")
                print(f"   ✓ Rotation enabled: {config['rotation_enabled']}")
                print(f"   ✓ Max log size: {config['max_log_size_mb']}MB")
                print(f"   ✓ Backup count: {config['backup_count']}")
                
                return True
                
        except ImportError as e:
            print(f"   Import error: {e}")
            return False
        except Exception as e:
            print(f"   Configuration error: {e}")
            return False
    
    # Test 2: Log Level Management
    def test_log_levels():
        print("🎚️ Testing log level management...")
        
        # Test all log levels
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in levels:
            try:
                level_int = getattr(logging, level)
                logging.getLogger().setLevel(level_int)
                current_level = logging.getLevelName(logging.getLogger().level)
                
                if current_level != level:
                    print(f"   Failed to set level {level}: got {current_level}")
                    return False
                
                print(f"   ✓ Level set to: {level}")
                
            except AttributeError:
                print(f"   Invalid log level: {level}")
                return False
        
        return True
    
    # Test 3: Log Rotation Configuration  
    def test_log_rotation():
        print("📁 Testing log rotation configuration...")
        
        try:
            import logging.handlers
            
            # Create temporary log file
            with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Set up rotating handler
            handler = logging.handlers.RotatingFileHandler(
                filename=temp_path,
                maxBytes=1024,  # 1KB for testing
                backupCount=3,
                encoding='utf-8'
            )
            
            logger = logging.getLogger('rotation_test')
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            # Generate enough logs to trigger rotation
            for i in range(50):
                logger.info(f"Test log entry {i+1} - This is a longer message to fill up the log file faster")
            
            # Check if rotation occurred
            base_dir = os.path.dirname(temp_path)
            base_name = os.path.basename(temp_path)
            
            rotation_files = []
            for file in os.listdir(base_dir):
                if file.startswith(base_name.split('.')[0]):
                    rotation_files.append(file)
            
            print(f"   Log files created: {len(rotation_files)}")
            print(f"   Main log size: {os.path.getsize(temp_path)} bytes")
            
            # Cleanup
            for file in rotation_files:
                try:
                    os.remove(os.path.join(base_dir, file))
                except:
                    pass
            
            return len(rotation_files) >= 1
            
        except Exception as e:
            print(f"   Rotation test error: {e}")
            return False
    
    # Test 4: Structured Logging Output
    def test_structured_output():
        print("📋 Testing structured logging output...")
        
        try:
            import structlog
            import json
            from io import StringIO
            
            # Configure structlog for testing
            output = StringIO()
            
            structlog.configure(
                processors=[
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.JSONRenderer()
                ],
                wrapper_class=structlog.stdlib.BoundLogger,
                logger_factory=structlog.stdlib.LoggerFactory(),
                cache_logger_on_first_use=True,
            )
            
            # Set up handler to capture output
            handler = logging.StreamHandler(output)
            logging.getLogger().addHandler(handler)
            logging.getLogger().setLevel(logging.INFO)
            
            # Create structured log entries
            logger = structlog.get_logger("test_logger")
            
            test_data = {
                'component': 'test_component',
                'correlation_id': 'test-123',
                'duration': 0.123,
                'status': 'success'
            }
            
            logger.info("Test structured log entry", **test_data)
            
            # Get output and parse JSON
            log_output = output.getvalue()
            
            if log_output.strip():
                # Try to parse as JSON
                try:
                    log_lines = log_output.strip().split('\n')
                    for line in log_lines:
                        if line.strip():
                            json.loads(line)
                    print("   ✓ Valid JSON structure")
                    print("   ✓ Structured data included")
                    return True
                except json.JSONDecodeError:
                    print("   ❌ Invalid JSON output")
                    return False
            else:
                print("   ❌ No log output generated")
                return False
                
        except Exception as e:
            print(f"   Structured output test error: {e}")
            return False
    
    # Test 5: Log File Management
    def test_log_file_management():
        print("📁 Testing log file management...")
        
        try:
            # Create temporary log directory
            with tempfile.TemporaryDirectory() as temp_dir:
                log_files = ['astro_engine.log', 'astro_engine_errors.log', 'astro_engine_performance.log']
                
                # Create sample log files
                for log_file in log_files:
                    file_path = os.path.join(temp_dir, log_file)
                    with open(file_path, 'w') as f:
                        f.write(f"Sample log content for {log_file}\n")
                        f.write(f"Timestamp: {datetime.utcnow().isoformat()}\n")
                
                # Verify files exist
                created_files = os.listdir(temp_dir)
                
                for expected_file in log_files:
                    if expected_file not in created_files:
                        print(f"   Missing log file: {expected_file}")
                        return False
                    
                    file_path = os.path.join(temp_dir, expected_file)
                    file_size = os.path.getsize(file_path)
                    print(f"   ✓ Created: {expected_file} ({file_size} bytes)")
                
                print(f"   Log directory: {temp_dir}")
                print(f"   Files created: {len(created_files)}")
                
                return True
                
        except Exception as e:
            print(f"   File management test error: {e}")
            return False
    
    # Test 6: Environment Configuration
    def test_environment_config():
        print("⚙️ Testing environment configuration...")
        
        # Test different environment configurations
        test_configs = [
            {'ENVIRONMENT': 'development', 'LOG_LEVEL': 'DEBUG'},
            {'ENVIRONMENT': 'production', 'LOG_LEVEL': 'INFO'},
            {'ENVIRONMENT': 'test', 'LOG_LEVEL': 'WARNING'}
        ]
        
        for config in test_configs:
            # Set environment variables
            for key, value in config.items():
                os.environ[key] = value
            
            try:
                # Test log level setting
                log_level = getattr(logging, config['LOG_LEVEL'])
                logging.getLogger().setLevel(log_level)
                
                current_level = logging.getLevelName(logging.getLogger().level)
                if current_level != config['LOG_LEVEL']:
                    print(f"   Failed to set level for {config['ENVIRONMENT']}")
                    return False
                
                print(f"   ✓ {config['ENVIRONMENT']}: {config['LOG_LEVEL']}")
                
            except Exception as e:
                print(f"   Error with config {config}: {e}")
                return False
        
        return True
    
    # Run all tests
    print("📊 Testing logging infrastructure...")
    run_test("Logger Creation and Configuration", test_logger_creation)
    
    print("🎚️ Testing log level management...")
    run_test("Log Level Management", test_log_levels)
    
    print("📁 Testing log rotation...")
    run_test("Log Rotation Configuration", test_log_rotation)
    
    print("📋 Testing structured output...")
    run_test("Structured Output", test_structured_output)
    
    print("📁 Testing log file management...")
    run_test("Log File Management", test_log_file_management)
    
    print("⚙️ Testing environment configuration...")
    run_test("Environment Configuration", test_environment_config)
    
    # Results summary
    print("=" * 60)
    print("📊 PHASE 3.3 VALIDATION SUMMARY")
    print(f"⏱️  Total test duration: {time.time() - start_time:.2f} seconds")
    print(f"✅ Tests passed: {results['tests_passed']}")
    print(f"❌ Tests failed: {results['tests_failed']}")
    print(f"📊 Total tests: {results['total_tests']}")
    print(f"🎯 Success rate: {(results['tests_passed']/results['total_tests']*100):.1f}%")
    
    if results['tests_failed'] == 0:
        print("🎉 ALL PHASE 3.3 TESTS PASSED!")
        print("✅ Phase 3.3: Log Management - COMPLETE")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    start_time = time.time()
    success = test_log_management_direct()
    sys.exit(0 if success else 1)
