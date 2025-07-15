"""
Configuration management for Rainbow Bridge
Centralized configuration handling with environment variables.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str = "sqlite:///special_kids.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class AIConfig:
    """AI service configuration settings."""
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo-instruct"
    max_tokens: int = 150
    temperature: float = 0.7
    use_local_llm: bool = False
    local_llm_url: str = "http://localhost:11434"
    local_llm_model: str = "llama2"


@dataclass
class MCPConfig:
    """MCP (Model Context Protocol) configuration settings."""
    server_host: str = "localhost"
    server_port: int = 3001
    client_timeout: float = 30.0
    max_retries: int = 3


@dataclass
class APIConfig:
    """API server configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class AppConfig:
    """Main application configuration."""
    database: DatabaseConfig
    ai: AIConfig
    mcp: MCPConfig
    api: APIConfig
    
    # Application settings
    app_name: str = "Rainbow Bridge"
    version: str = "1.3.0"
    description: str = "AI-powered companion for special needs children"
    
    # File paths
    static_dir: str = "static"
    templates_dir: str = "templates"
    logs_dir: str = "logs"
    uploads_dir: str = "uploads"


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    
    # Database configuration
    database_config = DatabaseConfig(
        url=os.getenv("DATABASE_URL", "sqlite:///special_kids.db"),
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )
    
    # AI configuration
    ai_config = AIConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-instruct"),
        max_tokens=int(os.getenv("AI_MAX_TOKENS", "150")),
        temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
        use_local_llm=os.getenv("USE_LOCAL_LLM", "false").lower() == "true",
        local_llm_url=os.getenv("LOCAL_LLM_URL", "http://localhost:11434"),
        local_llm_model=os.getenv("LOCAL_LLM_MODEL", "llama2")
    )
    
    # MCP configuration
    mcp_config = MCPConfig(
        server_host=os.getenv("MCP_HOST", "localhost"),
        server_port=int(os.getenv("MCP_PORT", "3001")),
        client_timeout=float(os.getenv("MCP_TIMEOUT", "30.0")),
        max_retries=int(os.getenv("MCP_RETRIES", "3"))
    )
    
    # API configuration
    api_config = APIConfig(
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )
    
    return AppConfig(
        database=database_config,
        ai=ai_config,
        mcp=mcp_config,
        api=api_config
    )


# Global configuration instance
config = load_config()
