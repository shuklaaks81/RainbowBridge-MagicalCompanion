# Migration Guide: From Legacy to Modular Architecture

This guide helps you transition from the legacy Rainbow Bridge structure to the new modular architecture.

## 🔄 Migration Overview

### What's Changed

1. **New Entry Point**: `app.py` (replaces `main.py`)
2. **Modular Structure**: Code organized in `src/` directory
3. **Centralized Configuration**: All settings in `config/settings.py`
4. **Organized Tests**: Tests moved to `tests/` directory
5. **Utility Scripts**: Scripts moved to `scripts/` directory

### Backward Compatibility

The legacy `main.py` still works for backward compatibility, but we recommend migrating to the new structure.

## 📁 File Mapping

### Old Structure → New Structure

```
# Entry Points
main.py                           → app.py

# Core Components
core/ai_assistant.py             → src/ai/assistant.py
core/routine_manager.py          → src/services/routine_service.py
core/routine_mcp_client.py       → src/mcp/client.py
database/db_manager.py           → src/services/database.py

# Models (extracted from various files)
[Various data classes]           → src/models/entities.py

# API Routes (extracted from main.py)
[FastAPI routes]                 → src/api/routes.py

# Utilities
[AI prompts, formatters]         → src/utils/

# Configuration
[Environment variables]          → config/settings.py

# Tests
test_*.py                        → tests/integration/
debug_*.py                       → tests/integration/

# Demo Scripts
demo_*.py                        → scripts/
```

## 🚀 Migration Steps

### Step 1: Update Your Development Workflow

**Old Way:**
```bash
python main.py
```

**New Way (Recommended):**
```bash
python app.py
```

### Step 2: Update Import Statements

**Old Imports:**
```python
from core.ai_assistant import AIAssistant
from database.db_manager import DatabaseManager
from core.routine_manager import RoutineManager
```

**New Imports:**
```python
from src.ai.assistant import AIAssistantService
from src.services.database import DatabaseService
from src.services.routine_service import RoutineService
```

### Step 3: Update Configuration Usage

**Old Way:**
```python
import os
api_key = os.getenv('OPENAI_API_KEY')
```

**New Way:**
```python
from config.settings import config
api_key = config.ai.openai_api_key
```

### Step 4: Update Test Execution

**Old Way:**
```bash
python test_final_general.py
python demo_fresh_setup.py
```

**New Way:**
```bash
python tests/integration/test_final_general.py
python scripts/demo_fresh_setup.py
```

## 🧪 Testing the Migration

### 1. Test Modular Structure
```bash
python tests/test_modular_structure.py
```

### 2. Test New Entry Point
```bash
python app.py
# Should start the server successfully
```

### 3. Test Legacy Compatibility
```bash
python main.py
# Should still work for backward compatibility
```

### 4. Run Demo Scripts
```bash
python scripts/demo_fresh_setup.py
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Make sure you're running from the project root directory and the `src/` directory has `__init__.py` files.

#### 2. Configuration Errors
**Problem:** Configuration not found

**Solution:** Ensure `.env` file exists and `config/settings.py` is properly imported.

#### 3. Database Issues
**Problem:** Database initialization fails

**Solution:** Check that the database file exists and permissions are correct.

### Debugging Tips

1. **Check Python Path:**
   ```python
   import sys
   print(sys.path)
   ```

2. **Verify Imports:**
   ```python
   from config.settings import config
   print(config.app_name)
   ```

3. **Test Components Individually:**
   ```bash
   python tests/test_modular_structure.py
   ```

## 📈 Benefits After Migration

### 1. **Better Organization**
- Clear separation of concerns
- Easier to find and modify code
- Better project navigation

### 2. **Improved Scalability**
- Easy to add new features
- Components can be developed independently
- Better team collaboration

### 3. **Enhanced Testing**
- Individual components can be tested
- Better test organization
- Easier mocking and isolation

### 4. **Configuration Management**
- Centralized configuration
- Environment-specific settings
- Type-safe configuration

### 5. **Development Experience**
- Better IDE support
- Clearer code structure
- Reduced cognitive load

## 🎯 Next Steps After Migration

1. **Update CI/CD pipelines** to use the new entry point
2. **Update documentation** to reflect new structure
3. **Create deployment scripts** using the new architecture
4. **Add monitoring and logging** using the new structure
5. **Implement additional features** using the modular approach

## 🔮 Future Enhancements

The new modular structure enables:

- **Microservices Architecture**: Split services into separate applications
- **Plugin System**: Add new features as plugins
- **API Versioning**: Support multiple API versions
- **Caching Layer**: Add Redis or similar caching
- **Background Tasks**: Add Celery or similar task queue
- **Database Migration**: Easy to switch to PostgreSQL or other databases

## 💬 Getting Help

If you encounter issues during migration:

1. Check the troubleshooting section above
2. Run the test script: `python tests/test_modular_structure.py`
3. Review the architecture documentation: `ARCHITECTURE.md`
4. Check the example code in `scripts/demo_fresh_setup.py`

Remember: The legacy structure still works, so you can migrate gradually! 🌈✨
