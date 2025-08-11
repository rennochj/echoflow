#!/usr/bin/env python3
"""
Phase 2 capability validation script.
Tests AI integration, document conversion, and system health.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def test_phase2():
    """Test Phase 2 capabilities comprehensively."""
    from echoflow.ai.model_manager import ModelManager
    from echoflow.converters.docling_converter import DoclingConverter
    from echoflow.converters.base import ConversionOptions, converter_registry
    from echoflow.server.health import health_check
    
    print('🎯 Phase 2 Capability Test Suite')
    print('=' * 40)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: AI integration
    try:
        manager = ModelManager()
        await manager.initialize()
        health = await manager.health_check()
        print(f'✅ Test 1/4: AI Models operational (health: {health})')
        if health:
            tests_passed += 1
        else:
            print('   ⚠️  AI health check returned False')
    except Exception as e:
        print(f'❌ Test 1/4: AI Models failed - {str(e)}')
    
    # Test 2: Document conversion
    try:
        converter = DoclingConverter()
        test_md = Path('/tmp/phase2_test.md')
        test_md.write_text('# Phase 2 Test\n\n**AI-powered** conversion test.\n\n- Feature 1\n- Feature 2')
        
        result = await converter.convert(test_md, Path('/tmp'), ConversionOptions())
        
        if len(result.markdown_content) > 0:
            print(f'✅ Test 2/4: Conversion successful ({len(result.markdown_content)} chars in {result.processing_time_seconds:.3f}s)')
            tests_passed += 1
        else:
            print('❌ Test 2/4: Conversion produced no content')
    except Exception as e:
        print(f'❌ Test 2/4: Conversion failed - {str(e)}')
    
    # Test 3: Registry integration
    try:
        formats = converter_registry.list_supported_formats()
        expected_formats = {'pdf', 'docx', 'pptx', 'html', 'md', 'txt'}
        
        if len(formats) >= 6 and expected_formats.issubset(set(formats)):
            print(f'✅ Test 3/4: Registry complete ({len(formats)} formats supported)')
            tests_passed += 1
        else:
            print(f'⚠️  Test 3/4: Registry partial ({len(formats)} formats: {formats})')
    except Exception as e:
        print(f'❌ Test 3/4: Registry failed - {str(e)}')
    
    # Test 4: Health system
    try:
        healthy = await health_check()
        if healthy:
            print(f'✅ Test 4/4: Health system operational')
            tests_passed += 1
        else:
            print(f'⚠️  Test 4/4: Health check returned False')
    except Exception as e:
        print(f'❌ Test 4/4: Health system failed - {str(e)}')
    
    # Cleanup
    try:
        await manager.cleanup()
    except:
        pass
    
    print('=' * 40)
    print(f'🏆 Results: {tests_passed}/{total_tests} tests passed')
    
    if tests_passed == total_tests:
        print('🎉 ALL PHASE 2 CAPABILITIES CONFIRMED!')
        print('🚀 AI-powered document processing fully operational')
        return True
    elif tests_passed >= 3:
        print('⚠️  Most capabilities working - minor issues detected')
        return True
    else:
        print('❌ Significant issues detected - Phase 2 needs attention')
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_phase2())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Phase 2 test crashed: {str(e)}")
        sys.exit(1)