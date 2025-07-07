"""
Local LLM Manager for Special Kids Assistant

This module provides support for various local LLM backends including:
- Ollama
- LocalAI
- Text Generation WebUI
- Hugging Face Transformers
- Custom OpenAI-compatible endpoints
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import requests
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class LocalLLMResponse:
    """Structure for local LLM response data."""
    text: str
    model: str
    processing_time: float
    success: bool
    error: Optional[str] = None

class LocalLLMProvider(ABC):
    """Abstract base class for local LLM providers."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 150,
        temperature: float = 0.7
    ) -> LocalLLMResponse:
        """Generate text using the local LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        pass

class OllamaProvider(LocalLLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2:7b-chat"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 150,
        temperature: float = 0.7
    ) -> LocalLLMResponse:
        """Generate text using Ollama."""
        import time
        start_time = time.time()
        
        try:
            # Combine system and user prompts for Ollama
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9
                }
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        processing_time = time.time() - start_time
                        
                        return LocalLLMResponse(
                            text=result.get("response", "").strip(),
                            model=self.model,
                            processing_time=processing_time,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        return LocalLLMResponse(
                            text="",
                            model=self.model,
                            processing_time=time.time() - start_time,
                            success=False,
                            error=f"HTTP {response.status}: {error_text}"
                        )
        
        except Exception as e:
            return LocalLLMResponse(
                text="",
                model=self.model,
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

class LocalAIProvider(LocalLLMProvider):
    """LocalAI provider."""
    
    def __init__(self, base_url: str = "http://localhost:8080", model: str = "gpt-3.5-turbo"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.api_key = os.getenv("LOCALAI_API_KEY", "not-needed")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 150,
        temperature: float = 0.7
    ) -> LocalLLMResponse:
        """Generate text using LocalAI."""
        import time
        start_time = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        processing_time = time.time() - start_time
                        
                        return LocalLLMResponse(
                            text=result["choices"][0]["message"]["content"].strip(),
                            model=self.model,
                            processing_time=processing_time,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        return LocalLLMResponse(
                            text="",
                            model=self.model,
                            processing_time=time.time() - start_time,
                            success=False,
                            error=f"HTTP {response.status}: {error_text}"
                        )
        
        except Exception as e:
            return LocalLLMResponse(
                text="",
                model=self.model,
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if LocalAI is running."""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False

class HuggingFaceProvider(LocalLLMProvider):
    """Hugging Face Transformers provider."""
    
    def __init__(self, model: str = "microsoft/DialoGPT-medium", device: str = "cpu"):
        self.model_name = model
        self.device = device
        self.tokenizer = None
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Hugging Face model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.to("cuda")
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info(f"Initialized Hugging Face model: {self.model_name}")
        
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face model: {e}")
            self.model = None
            self.tokenizer = None
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 150,
        temperature: float = 0.7
    ) -> LocalLLMResponse:
        """Generate text using Hugging Face model."""
        import time
        start_time = time.time()
        
        if not self.model or not self.tokenizer:
            return LocalLLMResponse(
                text="",
                model=self.model_name,
                processing_time=time.time() - start_time,
                success=False,
                error="Model not initialized"
            )
        
        try:
            # Combine prompts
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            # Tokenize input
            inputs = self.tokenizer.encode(full_prompt, return_tensors="pt")
            if self.device == "cuda" and inputs.device.type == "cpu":
                inputs = inputs.to("cuda")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=len(inputs[0]) + max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response[len(full_prompt):].strip()
            
            processing_time = time.time() - start_time
            
            return LocalLLMResponse(
                text=response,
                model=self.model_name,
                processing_time=processing_time,
                success=True
            )
        
        except Exception as e:
            return LocalLLMResponse(
                text="",
                model=self.model_name,
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if Hugging Face model is available."""
        return self.model is not None and self.tokenizer is not None

class LocalLLMManager:
    """Manager for local LLM providers."""
    
    def __init__(self):
        self.providers = {}
        self.primary_provider = None
        self.fallback_to_openai = os.getenv("FALLBACK_TO_OPENAI", "True").lower() == "true"
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available local LLM providers."""
        # Initialize Ollama if enabled
        if os.getenv("OLLAMA_ENABLED", "True").lower() == "true":
            ollama = OllamaProvider(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "llama2:7b-chat")
            )
            self.providers["ollama"] = ollama
        
        # Initialize LocalAI if enabled
        if os.getenv("LOCALAI_ENABLED", "False").lower() == "true":
            localai = LocalAIProvider(
                base_url=os.getenv("LOCALAI_BASE_URL", "http://localhost:8080"),
                model=os.getenv("LOCALAI_MODEL", "gpt-3.5-turbo")
            )
            self.providers["localai"] = localai
        
        # Initialize Hugging Face if enabled
        if os.getenv("HF_ENABLED", "False").lower() == "true":
            hf = HuggingFaceProvider(
                model=os.getenv("HF_MODEL", "microsoft/DialoGPT-medium"),
                device=os.getenv("HF_DEVICE", "cpu")
            )
            self.providers["huggingface"] = hf
        
        # Set primary provider
        primary = os.getenv("PRIMARY_LOCAL_LLM", "ollama")
        if primary in self.providers:
            self.primary_provider = self.providers[primary]
        elif self.providers:
            self.primary_provider = list(self.providers.values())[0]
        
        logger.info(f"Initialized local LLM providers: {list(self.providers.keys())}")
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = None,
        temperature: float = None
    ) -> LocalLLMResponse:
        """Generate response using available local LLM."""
        # Use environment defaults if not specified
        max_tokens = max_tokens or int(os.getenv("LOCAL_MAX_TOKENS", "150"))
        temperature = temperature or float(os.getenv("LOCAL_TEMPERATURE", "0.7"))
        
        # Apply content filtering for child safety
        if os.getenv("CHILD_SAFE_MODE", "True").lower() == "true":
            system_prompt = self._add_safety_prompt(system_prompt)
        
        # Try primary provider first
        if self.primary_provider and self.primary_provider.is_available():
            try:
                response = await self.primary_provider.generate(
                    prompt, system_prompt, max_tokens, temperature
                )
                if response.success:
                    return response
            except Exception as e:
                logger.warning(f"Primary provider failed: {e}")
        
        # Try other providers
        for name, provider in self.providers.items():
            if provider != self.primary_provider and provider.is_available():
                try:
                    response = await provider.generate(
                        prompt, system_prompt, max_tokens, temperature
                    )
                    if response.success:
                        logger.info(f"Used fallback provider: {name}")
                        return response
                except Exception as e:
                    logger.warning(f"Provider {name} failed: {e}")
        
        # Return error response if all providers failed
        return LocalLLMResponse(
            text="",
            model="none",
            processing_time=0,
            success=False,
            error="No local LLM providers available"
        )
    
    def _add_safety_prompt(self, system_prompt: str) -> str:
        """Add child safety instructions to system prompt."""
        safety_prompt = """
        
        IMPORTANT CHILD SAFETY GUIDELINES:
        - Always use age-appropriate, gentle language
        - Never discuss inappropriate topics
        - Focus on positive, encouraging communication
        - If asked about sensitive topics, redirect to appropriate activities
        - Maintain a safe, supportive environment for children
        """
        return system_prompt + safety_prompt
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [name for name, provider in self.providers.items() if provider.is_available()]
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers."""
        return {name: provider.is_available() for name, provider in self.providers.items()}
