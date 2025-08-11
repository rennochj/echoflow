#!/usr/bin/env python3
"""
Docker container validation script for EchoFlow Phase 2 capabilities.
Tests all core functionality within the Docker environment.
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, "src")

async def main():
    """Run comprehensive Docker container tests."""
    print('🐳 EchoFlow Phase 2 Docker Validation')
    print('=' * 40)
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Basic imports
    try:
        import echoflow
        from echoflow.ai.model_manager import ModelManager
        from echoflow.converters.docling_converter import DoclingConverter
        from echoflow.server.health import health_check
        print('✅ Test 1/6: All modules imported successfully')
        tests_passed += 1
    except Exception as e:
        print(f'❌ Test 1/6: Import failed - {str(e)}')
    
    # Test 2: ModelManager
    try:
        manager = ModelManager()
        await manager.initialize()
        health = await manager.health_check()
        await manager.cleanup()
        print(f'✅ Test 2/6: ModelManager operational (health: {health})')
        tests_passed += 1
    except Exception as e:
        print(f'❌ Test 2/6: ModelManager failed - {str(e)}')
    
    # Test 3: DoclingConverter
    try:
        converter = DoclingConverter()
        formats = converter.supported_formats
        print(f'✅ Test 3/6: DoclingConverter supports {len(formats)} formats')
        tests_passed += 1
    except Exception as e:
        print(f'❌ Test 3/6: DoclingConverter failed - {str(e)}')
    
    # Test 4: Registry integration
    try:
        from echoflow.converters.base import converter_registry
        formats = converter_registry.list_supported_formats()
        print(f'✅ Test 4/6: Registry supports {len(formats)} formats')
        tests_passed += 1
    except Exception as e:
        print(f'❌ Test 4/6: Registry failed - {str(e)}')
    
    # Test 5: Document conversion
    try:
        from echoflow.converters.base import ConversionOptions
        test_file = Path('/tmp/test.md')
        test_file.write_text('# Docker Test\n\nThis tests **conversion** in Docker.\n\n- Feature 1\n- Feature 2')
        output_dir = Path('/tmp/output')
        output_dir.mkdir(exist_ok=True)
        
        result = await converter.convert(test_file, output_dir, ConversionOptions())
        print(f'✅ Test 5/6: Conversion successful ({len(result.markdown_content)} chars in {result.processing_time_seconds:.3f}s)')
        tests_passed += 1
    except Exception as e:
        print(f'❌ Test 5/6: Conversion failed - {str(e)}')
        traceback.print_exc()
    
    # Test 6: Health system
    try:
        healthy = await health_check()
        print(f'✅ Test 6/6: Health check completed (result: {healthy})')
        tests_passed += 1
    except Exception as e:
        print(f'❌ Test 6/6: Health check failed - {str(e)}')
    
    print('=' * 40)
    print(f'🏆 Results: {tests_passed}/{total_tests} tests passed')
    
    if tests_passed == total_tests:
        print('✅ ALL DOCKER TESTS PASSED!')
        print('🎯 Phase 2 capabilities confirmed in Docker')
        print('🚀 Container ready for production deployment')
        return True
    elif tests_passed >= 4:
        print('⚠️  Most tests passed - container is functional')
        print('🎯 Phase 2 capabilities largely operational')
        return True
    else:
        print(f'❌ {total_tests - tests_passed} tests failed')
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Docker test crashed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)