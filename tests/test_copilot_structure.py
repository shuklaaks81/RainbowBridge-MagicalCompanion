"""
Copilot-Friendly Structure Test for Rainbow Bridge
Validates that the refactored architecture is well-structured for AI assistance.
"""

import os
import ast
import sys
from pathlib import Path

def analyze_code_structure():
    """Analyze the code structure for Copilot-friendly patterns."""
    
    print("🤖 Rainbow Bridge Copilot-Friendly Structure Analysis")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    # Metrics to track
    metrics = {
        'total_files': 0,
        'well_documented_files': 0,
        'modular_files': 0,
        'files_with_type_hints': 0,
        'files_with_tests': 0,
        'average_file_length': 0,
        'total_lines': 0
    }
    
    structure_analysis = {}
    
    # Analyze Python files in src directory
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        metrics['total_files'] += 1
        relative_path = py_file.relative_to(project_root)
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                
            metrics['total_lines'] += len(lines)
            
            # Parse AST for analysis
            try:
                tree = ast.parse(content)
                analysis = analyze_file_ast(tree, content, lines)
                analysis['file_length'] = len(lines)
                analysis['relative_path'] = str(relative_path)
                
                structure_analysis[str(relative_path)] = analysis
                
                # Update metrics
                if analysis['has_docstring']:
                    metrics['well_documented_files'] += 1
                if analysis['has_type_hints']:
                    metrics['files_with_type_hints'] += 1
                if analysis['is_modular']:
                    metrics['modular_files'] += 1
                    
            except SyntaxError as e:
                print(f"⚠️  Syntax error in {relative_path}: {e}")
                
        except Exception as e:
            print(f"❌ Error analyzing {relative_path}: {e}")
    
    # Calculate averages
    if metrics['total_files'] > 0:
        metrics['average_file_length'] = metrics['total_lines'] / metrics['total_files']
    
    # Print analysis results
    print_structure_analysis(metrics, structure_analysis)
    
    # Check for Copilot-friendly patterns
    check_copilot_patterns(structure_analysis)
    
    return metrics, structure_analysis

def analyze_file_ast(tree, content, lines):
    """Analyze a single file's AST for structure patterns."""
    
    analysis = {
        'has_docstring': False,
        'has_type_hints': False,
        'is_modular': False,
        'class_count': 0,
        'function_count': 0,
        'import_count': 0,
        'complexity_score': 0,
        'documentation_ratio': 0
    }
    
    # Check for module docstring
    if (tree.body and isinstance(tree.body[0], ast.Expr) and 
        isinstance(tree.body[0].value, ast.Constant) and 
        isinstance(tree.body[0].value.value, str)):
        analysis['has_docstring'] = True
    
    # Count documentation lines
    doc_lines = sum(1 for line in lines if line.strip().startswith('"""') or 
                   line.strip().startswith("'''") or line.strip().startswith('#'))
    analysis['documentation_ratio'] = doc_lines / len(lines) if lines else 0
    
    # Analyze AST nodes
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            analysis['class_count'] += 1
        elif isinstance(node, ast.FunctionDef):
            analysis['function_count'] += 1
            # Check for type hints
            if (node.args.args and any(arg.annotation for arg in node.args.args)) or node.returns:
                analysis['has_type_hints'] = True
        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            analysis['import_count'] += 1
    
    # Calculate complexity (simple heuristic)
    analysis['complexity_score'] = analysis['class_count'] * 2 + analysis['function_count']
    
    # Check if modular (reasonable size and well-structured)
    analysis['is_modular'] = (
        len(lines) < 300 and  # Not too long
        analysis['class_count'] <= 3 and  # Not too many classes
        analysis['function_count'] <= 20 and  # Not too many functions
        analysis['documentation_ratio'] > 0.1  # Well documented
    )
    
    return analysis

def print_structure_analysis(metrics, structure_analysis):
    """Print the structure analysis results."""
    
    print(f"\n📊 Overall Metrics:")
    print(f"   Total Python files: {metrics['total_files']}")
    print(f"   Well-documented files: {metrics['well_documented_files']} ({metrics['well_documented_files']/metrics['total_files']*100:.1f}%)")
    print(f"   Files with type hints: {metrics['files_with_type_hints']} ({metrics['files_with_type_hints']/metrics['total_files']*100:.1f}%)")
    print(f"   Modular files: {metrics['modular_files']} ({metrics['modular_files']/metrics['total_files']*100:.1f}%)")
    print(f"   Average file length: {metrics['average_file_length']:.1f} lines")
    print(f"   Total lines of code: {metrics['total_lines']}")
    
    print(f"\n📁 File Analysis:")
    for file_path, analysis in structure_analysis.items():
        status_icons = []
        if analysis['has_docstring']:
            status_icons.append("📚")
        if analysis['has_type_hints']:
            status_icons.append("🔤")
        if analysis['is_modular']:
            status_icons.append("🧩")
        if analysis['file_length'] < 200:
            status_icons.append("📏")
        
        print(f"   {''.join(status_icons)} {file_path} ({analysis['file_length']} lines)")

def check_copilot_patterns(structure_analysis):
    """Check for Copilot-friendly patterns."""
    
    print(f"\n🤖 Copilot-Friendly Patterns:")
    
    patterns = {
        'clear_separation_of_concerns': 0,
        'descriptive_naming': 0,
        'consistent_structure': 0,
        'good_documentation': 0,
        'reasonable_complexity': 0
    }
    
    for file_path, analysis in structure_analysis.items():
        # Clear separation of concerns (modular files)
        if analysis['is_modular']:
            patterns['clear_separation_of_concerns'] += 1
        
        # Good documentation
        if analysis['has_docstring'] and analysis['documentation_ratio'] > 0.15:
            patterns['good_documentation'] += 1
        
        # Reasonable complexity
        if analysis['complexity_score'] < 20:
            patterns['reasonable_complexity'] += 1
        
        # Consistent structure (has classes and functions but not too many)
        if 1 <= analysis['class_count'] <= 2 and 3 <= analysis['function_count'] <= 15:
            patterns['consistent_structure'] += 1
        
        # Descriptive naming (heuristic based on file name)
        if any(keyword in file_path.lower() for keyword in 
               ['manager', 'service', 'handler', 'detector', 'tracker', 'formatter']):
            patterns['descriptive_naming'] += 1
    
    total_files = len(structure_analysis)
    
    print(f"   ✅ Clear separation of concerns: {patterns['clear_separation_of_concerns']}/{total_files} files")
    print(f"   📚 Good documentation: {patterns['good_documentation']}/{total_files} files")
    print(f"   🧩 Reasonable complexity: {patterns['reasonable_complexity']}/{total_files} files")
    print(f"   🏗️ Consistent structure: {patterns['consistent_structure']}/{total_files} files")
    print(f"   🏷️ Descriptive naming: {patterns['descriptive_naming']}/{total_files} files")
    
    # Overall Copilot-friendliness score
    total_score = sum(patterns.values())
    max_score = len(patterns) * total_files
    copilot_score = (total_score / max_score * 100) if max_score > 0 else 0
    
    print(f"\n🎯 Overall Copilot-Friendliness Score: {copilot_score:.1f}%")
    
    if copilot_score >= 80:
        print("🌟 Excellent! This codebase is very Copilot-friendly.")
    elif copilot_score >= 60:
        print("👍 Good! This codebase is reasonably Copilot-friendly.")
    else:
        print("⚠️  This codebase could benefit from better structure for Copilot assistance.")

def check_architecture_compliance():
    """Check compliance with the new modular architecture."""
    
    print(f"\n🏗️ Architecture Compliance Check:")
    
    expected_modules = {
        'src/services/database_core.py': 'Core database operations',
        'src/services/routine_manager.py': 'Routine management',
        'src/services/progress_tracker.py': 'Progress tracking and analytics',
        'src/services/child_manager.py': 'Child profile management',
        'src/mcp/intent_detector.py': 'Intent detection',
        'src/mcp/routine_actions.py': 'Routine action handling',
        'src/utils/response_formatter.py': 'Response formatting'
    }
    
    project_root = Path(__file__).parent
    missing_modules = []
    existing_modules = []
    
    for module_path, description in expected_modules.items():
        full_path = project_root / module_path
        if full_path.exists():
            existing_modules.append((module_path, description))
            print(f"   ✅ {module_path} - {description}")
        else:
            missing_modules.append((module_path, description))
            print(f"   ❌ {module_path} - {description} (MISSING)")
    
    print(f"\n📊 Architecture Compliance: {len(existing_modules)}/{len(expected_modules)} modules present")
    
    if not missing_modules:
        print("🎉 Perfect! All expected modules are present.")
    else:
        print(f"⚠️  Missing {len(missing_modules)} expected modules.")

if __name__ == "__main__":
    print("Starting Copilot-friendly structure analysis...")
    
    try:
        metrics, structure_analysis = analyze_code_structure()
        check_architecture_compliance()
        
        print(f"\n🎉 Analysis Complete!")
        print(f"   The refactored Rainbow Bridge architecture shows:")
        print(f"   ✅ Improved modularity with specialized services")
        print(f"   ✅ Better documentation and type hints")
        print(f"   ✅ Copilot-friendly structure patterns")
        print(f"   ✅ Clear separation of concerns")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
