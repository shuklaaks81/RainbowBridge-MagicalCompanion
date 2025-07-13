# Azure OpenAI Setup Guide for Rainbow Bridge

## 🌈 Azure OpenAI Integration Complete!

Your Azure OpenAI has been configured with the following settings:

### Current Configuration:
- **API Key**: ✅ Configured
- **Endpoint**: ✅ `https://aistatrter.openai.azure.com/`
- **API Version**: `2024-02-15-preview`
- **Deployment Name**: `gpt-4` (⚠️ **This needs to be verified**)

## 🔧 Next Steps to Complete Setup:

### 1. Verify Your Deployment Name
The most critical step is to set the correct deployment name. In your Azure OpenAI Studio:

1. Go to [Azure OpenAI Studio](https://oai.azure.com/)
2. Navigate to **Deployments** in the left sidebar
3. Find your GPT-4 deployment name (it might be different from "gpt-4")
4. Update the `.env` file with the exact deployment name:

```bash
AZURE_OPENAI_DEPLOYMENT_NAME=your-actual-deployment-name
```

### 2. Common Deployment Names:
- `gpt-4`
- `gpt-4-32k`
- `gpt-4-1106-preview`
- `gpt-35-turbo`
- Custom names you've created

### 3. Test the Connection:
After updating the deployment name, run:
```bash
python test_azure_openai.py
```

### 4. Alternative: Quick Deployment Check
You can also test your deployment with a simple curl command:
```bash
curl -X POST "https://aistatrter.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME/chat/completions?api-version=2024-02-15-preview" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_AZURE_OPENAI_API_KEY" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 10
  }'
```

Replace `YOUR_DEPLOYMENT_NAME` with your actual deployment name.

## 🚀 Features Ready:

Once the deployment name is correct, your Rainbow Bridge application will have:

- ✅ Azure OpenAI integration for autism-friendly communication
- ✅ Sensory-friendly AI responses
- ✅ Visual communication support
- ✅ Routine and schedule assistance
- ✅ Personalized learning adaptation
- ✅ Fallback to local LLM if needed

## 🎯 Application Usage:

After setup, you can start the application with:
```bash
python main.py
```

Then visit `http://localhost:8000` to access the Rainbow Bridge interface.

## 🔍 Troubleshooting:

### Common Issues:
1. **Connection Error**: Check deployment name and endpoint
2. **Authentication Error**: Verify API key
3. **Rate Limiting**: Azure OpenAI has usage limits

### Support:
- Check Azure OpenAI documentation
- Verify your Azure subscription has OpenAI access
- Ensure the deployment is in the same region as your endpoint

## 📝 Current Environment Variables:
```
LOCAL_MODE=False
USE_AZURE_OPENAI=True
AZURE_OPENAI_API_KEY=AZ*** (configured)
AZURE_OPENAI_ENDPOINT=https://aistatrter.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4 (⚠️ verify this)
```

**The main thing to check now is the deployment name in your Azure OpenAI Studio!**
