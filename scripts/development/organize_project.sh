#!/bin/bash
# FINAL ORGANIZATION SCRIPT FOR ASTRO ENGINE

echo "🚀 ORGANIZING ASTRO ENGINE PROJECT STRUCTURE"
echo "=============================================="

cd "/Users/apple/Documents/astro engine test/Astro_Engine"

# Create organized structure
mkdir -p docs/{deployment,development,planning}
mkdir -p tests/{integration,performance,validation}
mkdir -p scripts/development
mkdir -p config

echo "📁 Moving documentation files..."
# Move documentation
mv FINAL_DEPLOYMENT_SUMMARY.md FINAL_DEPLOYMENT_VALIDATION.md PRODUCTION_DEPLOYMENT_SUMMARY.md DEPLOYMENT_STATUS.md DIGITALOCEAN_DEPLOYMENT.md PRODUCTION_CHECKLIST.md docs/deployment/ 2>/dev/null
mv IMPLEMENTATION_PROGRESS_TRACKER.md PERFORMANCE_ENHANCEMENT_DETAILED_PLAN.md PERFORMANCE_ENHANCEMENT_PLAN.md REDIS_CONFIGURATION.md REDIS_IMPLEMENTATION_PLAN.md docs/development/ 2>/dev/null
mv ASTRO_RATAN_INTEGRATION.md CORPORATE_ENDPOINTS.md DATABASE_ARCHITECTURE_ANALYSIS.md PREDICTIVE_ALGORITHMS.md PROJECT_COMPLETION.md TEAM_ONBOARDING.md docs/planning/ 2>/dev/null

echo "🧪 Moving test files..."
# Move test files
mv test_*.py tests/ 2>/dev/null
mv *validation*.py production_readiness_check.py debug_cache.py quick_test.py simple_health_check.py tests/validation/ 2>/dev/null
mv phase1_integration_test.py manual_phase2_2_test.py tests/integration/ 2>/dev/null

echo "🛠️ Moving scripts..."
# Move scripts
mv start_*.sh quick_start.sh run_server.py start_celery_worker.py scripts/development/ 2>/dev/null

echo "⚙️ Moving config files..."
# Move config files
mv gunicorn.conf.py nginx.conf config/ 2>/dev/null

echo "🧹 Cleaning up..."
# Clean up old files
rm -f *.log nohup.out api_test_report.json ultimate_validation_report.json 2>/dev/null
rm -f deploy.sh ultimate_deploy.sh verify_deployment.py 2>/dev/null

echo ""
echo "✅ ORGANIZATION COMPLETE!"
echo "📊 Final structure:"
echo "   📱 astro_engine/     - Core application"
echo "   🚀 deployment/      - Cloud deployment configs"
echo "   📖 docs/           - Organized documentation"
echo "   🧪 tests/          - Comprehensive test suite"
echo "   🛠️ scripts/        - Development utilities"
echo "   ⚙️ config/         - Configuration files"
echo ""
echo "🎉 Project is now professionally organized!"
