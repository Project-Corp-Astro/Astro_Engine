#!/usr/bin/env python3
"""
Simple test server for Redis caching validation
Tests core functionality without complex imports
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
import time
import json
import hashlib
from cache_manager import create_cache_manager

app = Flask(__name__)

# Initialize cache
cache_manager = create_cache_manager(app)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'cache_available': cache_manager.is_available()
    })

@app.route('/cache/stats')
def cache_stats():
    """Get cache statistics"""
    return jsonify(cache_manager.get_stats())

@app.route('/cache/clear', methods=['DELETE'])
def clear_cache():
    """Clear all cache"""
    success = cache_manager.clear_all()
    return jsonify({'success': success})

def cached_calculation(cache_key, calculation_func, *args, **kwargs):
    """Helper function for cached calculations"""
    # Try to get from cache
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        return cached_result
    
    # Calculate and cache
    start_time = time.time()
    result = calculation_func(*args, **kwargs)
    calculation_time = time.time() - start_time
    
    # Add performance metadata
    result['_performance'] = {
        'calculation_time': calculation_time,
        'cached': False,
        'timestamp': time.time()
    }
    
    # Store in cache
    cache_manager.set(cache_key, result, 3600)  # 1 hour TTL
    
    return result

def simulate_natal_calculation(birth_data):
    """Simulate a natal chart calculation"""
    # Simulate calculation time
    time.sleep(0.5)  # Simulate 500ms calculation
    
    return {
        'user_name': birth_data.get('user_name', 'Unknown'),
        'birth_details': birth_data,
        'planetary_positions': {
            'Sun': {'sign': 'Capricorn', 'degrees': '10°23\'45"', 'house': 1},
            'Moon': {'sign': 'Cancer', 'degrees': '22°14\'32"', 'house': 7},
            'Mars': {'sign': 'Aries', 'degrees': '05°47\'21"', 'house': 4},
            'Mercury': {'sign': 'Sagittarius', 'degrees': '28°56\'12"', 'house': 12},
            'Jupiter': {'sign': 'Virgo', 'degrees': '13°29\'56"', 'house': 9},
            'Venus': {'sign': 'Aquarius', 'degrees': '19°35\'43"', 'house': 2},
            'Saturn': {'sign': 'Scorpio', 'degrees': '02°18\'29"', 'house': 11},
            'Rahu': {'sign': 'Gemini', 'degrees': '07°42\'18"', 'house': 6},
            'Ketu': {'sign': 'Sagittarius', 'degrees': '07°42\'18"', 'house': 12}
        },
        'ascendant': {
            'sign': 'Capricorn',
            'degrees': '15°32\'28"'
        }
    }

def simulate_navamsa_calculation(birth_data):
    """Simulate a navamsa chart calculation"""
    # Simulate calculation time
    time.sleep(0.3)  # Simulate 300ms calculation
    
    return {
        'user_name': birth_data.get('user_name', 'Unknown'),
        'd9_chart': {
            'Sun': {'sign': 'Leo', 'degrees': '25°14\'32"', 'house': 3},
            'Moon': {'sign': 'Pisces', 'degrees': '08°47\'21"', 'house': 8},
            'Mars': {'sign': 'Cancer', 'degrees': '16°35\'43"', 'house': 12},
            'Mercury': {'sign': 'Gemini', 'degrees': '03°18\'29"', 'house': 11},
            'Jupiter': {'sign': 'Sagittarius', 'degrees': '21°42\'18"', 'house': 5},
            'Venus': {'sign': 'Libra', 'degrees': '12°56\'12"', 'house': 4},
            'Saturn': {'sign': 'Aquarius', 'degrees': '29°29\'56"', 'house': 7},
            'Rahu': {'sign': 'Virgo', 'degrees': '18°23\'45"', 'house': 2},
            'Ketu': {'sign': 'Pisces', 'degrees': '18°23\'45"', 'house': 8}
        }
    }

@app.route('/test/natal', methods=['POST'])
def test_natal():
    """Test natal chart calculation with caching"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate cache key
        cache_key = cache_manager.generate_cache_key(data, 'natal_test')
        
        # Get cached or calculate
        result = cached_calculation(cache_key, simulate_natal_calculation, data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test/navamsa', methods=['POST'])
def test_navamsa():
    """Test navamsa chart calculation with caching"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate cache key
        cache_key = cache_manager.generate_cache_key(data, 'navamsa_test')
        
        # Get cached or calculate
        result = cached_calculation(cache_key, simulate_navamsa_calculation, data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test/performance', methods=['POST'])
def test_performance():
    """Test endpoint for performance validation"""
    try:
        data = request.get_json()
        iterations = data.get('iterations', 5)
        endpoint = data.get('endpoint', 'natal')
        
        test_data = {
            'user_name': 'Performance Test',
            'birth_date': '1990-01-01',
            'birth_time': '12:00:00',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'timezone_offset': 5.5
        }
        
        results = []
        
        for i in range(iterations):
            start_time = time.time()
            
            if endpoint == 'natal':
                cache_key = cache_manager.generate_cache_key(test_data, 'natal_perf')
                result = cached_calculation(cache_key, simulate_natal_calculation, test_data)
            else:
                cache_key = cache_manager.generate_cache_key(test_data, 'navamsa_perf')
                result = cached_calculation(cache_key, simulate_navamsa_calculation, test_data)
            
            end_time = time.time()
            
            results.append({
                'iteration': i + 1,
                'response_time': end_time - start_time,
                'cached': result.get('_performance', {}).get('cached', False),
                'calculation_time': result.get('_performance', {}).get('calculation_time', 0)
            })
        
        # Calculate performance metrics
        times = [r['response_time'] for r in results]
        first_call = times[0]
        cached_calls = times[1:] if len(times) > 1 else []
        avg_cached = sum(cached_calls) / len(cached_calls) if cached_calls else first_call
        
        improvement = ((first_call - avg_cached) / first_call) * 100 if first_call > 0 else 0
        
        return jsonify({
            'endpoint': endpoint,
            'iterations': iterations,
            'results': results,
            'performance': {
                'first_call_time': first_call,
                'avg_cached_time': avg_cached,
                'improvement_percent': improvement,
                'cache_hits': len([r for r in results if r.get('cached')])
            },
            'cache_stats': cache_manager.get_stats()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Redis Cache Test Server")
    print(f"Cache available: {cache_manager.is_available()}")
    print("Test endpoints:")
    print("  POST /test/natal - Test natal chart caching")
    print("  POST /test/navamsa - Test navamsa chart caching")
    print("  POST /test/performance - Performance testing")
    print("  GET /cache/stats - Cache statistics")
    print("  DELETE /cache/clear - Clear cache")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
