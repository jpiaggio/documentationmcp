"""
Tests for Caching Intelligence System

Tests cover:
- Git history analysis
- Dependency graph building
- Change prioritization
- Smart predictions
- Integration with CartographerAgent
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.cache_intelligence import (
    GitHistoryAnalyzer,
    DependencyGraphBuilder,
    ChangePrioritizer,
    SmartCachePredictor,
    CacheIntelligenceManager
)


class TestDependencyGraphBuilder:
    """Test dependency graph construction"""
    
    def test_python_import_extraction(self):
        """Test extracting Python imports"""
        builder = DependencyGraphBuilder('.')
        
        # Test 'import X' format
        code1 = "import os\nimport sys\nfrom pathlib import Path"
        imports1 = builder._extract_python_imports(code1, 'test.py')
        assert 'os' in imports1
        assert 'sys' in imports1
        assert 'pathlib' in imports1
        print("✓ Python import extraction works")
    
    def test_java_import_extraction(self):
        """Test extracting Java imports"""
        builder = DependencyGraphBuilder('.')
        
        code = """
        import java.util.ArrayList;
        import java.io.File;
        import org.springframework.boot.SpringApplication;
        """
        imports = builder._extract_java_imports(code, 'Test.java')
        assert 'java.util' in imports
        assert 'java.io' in imports
        assert 'org.springframework.boot' in imports
        print("✓ Java import extraction works")
    
    def test_module_name_extraction(self):
        """Test extracting module names from paths"""
        builder = DependencyGraphBuilder('.')
        
        py_name = builder._get_module_name('/path/to/parser.py', 'python')
        assert py_name == 'parser'
        
        java_name = builder._get_module_name('/path/to/Parser.java', 'java')
        assert java_name == 'Parser'
        print("✓ Module name extraction works")


class TestChangePrioritizer:
    """Test change prioritization"""
    
    def test_change_score_calculation(self):
        """Test priority score calculation"""
        analyzer = None
        dependency_graph = {'file1.py': set(['file2.py', 'file3.py'])}
        
        prioritizer = ChangePrioritizer(analyzer, dependency_graph)
        
        # High frequency, should get high score
        frequency_data = {'file1.py': 10}
        score = prioritizer.calculate_change_score('file1.py', frequency_data)
        assert score > 10  # frequency * 2.0 at minimum
        print(f"✓ Change score calculation works (score: {score:.1f})")
    
    def test_impact_score_calculation(self):
        """Test impact score for dependent files"""
        analyzer = None
        dependency_graph = {}
        prioritizer = ChangePrioritizer(analyzer, dependency_graph)
        
        # 5 dependent files
        impact = prioritizer.calculate_impact_score('core.py', 5)
        assert impact > 0
        assert impact <= 10  # Capped at 10
        print(f"✓ Impact score calculation works (impact: {impact:.1f})")
    
    def test_file_prioritization(self):
        """Test prioritizing multiple files"""
        analyzer = None
        dependency_graph = {
            'file1.py': set(['file2.py']),
            'file2.py': set(['file3.py']),
        }
        prioritizer = ChangePrioritizer(analyzer, dependency_graph)
        
        files = ['file1.py', 'file2.py', 'file3.py']
        frequency_data = {'file1.py': 5, 'file2.py': 3, 'file3.py': 1}
        
        prioritized = prioritizer.prioritize_files(files, frequency_data)
        assert prioritized[0][0] == 'file1.py'  # Most frequent
        print("✓ File prioritization works")


class TestGitHistoryAnalyzer:
    """Test git history analysis (requires git repo)"""
    
    @staticmethod
    def is_git_repo(path):
        """Check if path is a git repository"""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=path,
                capture_output=True,
                timeout=5,
                check=True
            )
            return True
        except Exception:
            return False
    
    def test_git_availability(self):
        """Check if we can test git functionality"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not self.is_git_repo(current_dir):
            print("⊘ Git repository not available, skipping git tests")
            return False
        return True
    
    def test_file_commit_history(self):
        """Test getting commit history"""
        if not self.test_git_availability():
            return
        
        repo = os.path.dirname(os.path.abspath(__file__))
        analyzer = GitHistoryAnalyzer(repo)
        
        # Get some test file from agents directory
        test_files = []
        agents_dir = os.path.join(repo, 'agents')
        if os.path.exists(agents_dir):
            for f in os.listdir(agents_dir):
                if f.endswith('.py'):
                    test_files.append(os.path.join(agents_dir, f))
        
        if test_files:
            test_file = test_files[0]
            history = analyzer.get_file_commit_history(test_file, max_commits=10)
            print(f"✓ Got commit history for {os.path.basename(test_file)}: {len(history)} commits")
    
    def test_change_frequency_analysis(self):
        """Test analyzing change frequency"""
        if not self.test_git_availability():
            return
        
        repo = os.path.dirname(os.path.abspath(__file__))
        analyzer = GitHistoryAnalyzer(repo)
        
        frequency = analyzer.analyze_change_frequency(['.py'], days=30)
        print(f"✓ Analyzed change frequency: {len(frequency)} files changed in last 30 days")


class TestSmartCachePredictor:
    """Test smart cache prediction"""
    
    def test_intelligence_data_persistence(self):
        """Test saving and loading intelligence data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            predictor = SmartCachePredictor(tmpdir)
            
            # Set some data
            test_data = {
                'cochange_patterns': {'file1.py': {'file2.py': 5}},
                'frequency_data': {'file1.py': 10}
            }
            predictor.intelligence_data.update(test_data)
            predictor._save_intelligence_data()
            
            # Load fresh predictor
            predictor2 = SmartCachePredictor(tmpdir)
            assert predictor2.intelligence_data.get('cochange_patterns') is not None
            print("✓ Intelligence data persistence works")
    
    def test_cache_directory_creation(self):
        """Test that cache directory is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            predictor = SmartCachePredictor(tmpdir)
            cache_dir = os.path.join(tmpdir, '.cartographer_cache')
            assert os.path.exists(cache_dir)
            print("✓ Cache directory creation works")


class TestCacheIntelligenceManager:
    """Test the high-level manager"""
    
    def test_manager_initialization(self):
        """Test manager creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CacheIntelligenceManager(tmpdir)
            assert manager.predictor is not None
            print("✓ Manager initialization works")
    
    def test_status_reporting(self):
        """Test status reporting"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CacheIntelligenceManager(tmpdir)
            status = manager.get_status()
            
            assert 'initialized' in status
            assert 'last_analyzed' in status
            assert 'cochange_patterns' in status
            print(f"✓ Status reporting works: {status}")


class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            os.makedirs(os.path.join(tmpdir, 'src'), exist_ok=True)
            
            # Create some test Python files
            file1 = os.path.join(tmpdir, 'src', 'main.py')
            with open(file1, 'w') as f:
                f.write('import os\nimport sys\nfrom utils import helper\n')
            
            file2 = os.path.join(tmpdir, 'src', 'utils.py')
            with open(file2, 'w') as f:
                f.write('import os\n')
            
            # Initialize git
            try:
                subprocess.run(['git', 'init'], cwd=tmpdir, capture_output=True, check=True)
                subprocess.run(['git', 'config', 'user.email', 'test@test.com'], 
                             cwd=tmpdir, capture_output=True)
                subprocess.run(['git', 'config', 'user.name', 'Test User'],
                             cwd=tmpdir, capture_output=True)
                subprocess.run(['git', 'add', '.'], cwd=tmpdir, capture_output=True)
                subprocess.run(['git', 'commit', '-m', 'initial'], 
                             cwd=tmpdir, capture_output=True)
            except Exception as e:
                print(f"⊘ Could not initialize git: {e}")
                return
            
            # Test workflow
            manager = CacheIntelligenceManager(tmpdir)
            all_files = [file1, file2]
            
            # Initialize
            result = manager.initialize_intelligence(all_files)
            print(f"✓ Initialization result: {result}")
            
            # Get plan
            plan = manager.get_smart_analysis_plan([file1], all_files, 'python')
            assert 'predicted_analyses' in plan
            print(f"✓ Got analysis plan with {len(plan['predicted_analyses'])} predictions")


def run_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CACHING INTELLIGENCE TESTS")
    print("=" * 60 + "\n")
    
    test_classes = [
        TestDependencyGraphBuilder,
        TestChangePrioritizer,
        TestGitHistoryAnalyzer,
        TestSmartCachePredictor,
        TestCacheIntelligenceManager,
        TestIntegration,
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        print("-" * 40)
        
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    method = getattr(instance, method_name)
                    method()
                    passed += 1
                except AssertionError as e:
                    print(f"✗ {method_name} failed: {e}")
                    failed += 1
                except Exception as e:
                    print(f"✗ {method_name} error: {e}")
                    failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
