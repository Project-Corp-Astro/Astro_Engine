#!/usr/bin/env python3
"""
Simple server runner that handles imports correctly
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the app
from astro_engine.app import app

if __name__ == "__main__":
    print("🚀 Starting Astro Engine Server...")
    print("🔗 Server will be available at: http://localhost:5001")
    print("📊 Health check: http://localhost:5001/health")
    print("📈 Cache stats: http://localhost:5001/cache/stats")
    print("⚡ Endpoints: /lahiri/natal, /lahiri/navamsa, /lahiri/calculate_d3, /lahiri/transit")
    print("=" * 80)
    
    app.run(debug=False, host='127.0.0.1', port=5001)
