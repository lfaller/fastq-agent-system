"""Base agent class for FASTQ analysis system."""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import anthropic
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Configuration for agents."""
    
    api_key: Optional[str] = None
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 500  # Reduced for faster responses
    temperature: float = 0.1


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        
        # Initialize Anthropic client
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment or config")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.name = self.__class__.__name__
    
    async def query_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Query the LLM with a prompt."""
        import time
        
        start_time = time.time()
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt or self.get_system_prompt(),
                messages=messages
            )
            # Extract text content with proper type handling
            content_block = response.content[0]
            result = str(content_block.text)
            
            # Log performance for monitoring
            elapsed = time.time() - start_time
            if elapsed > 5.0:  # Only log slow queries
                self.log(f"LLM query completed in {elapsed:.2f}s")
            
            return result
        except Exception as e:
            raise RuntimeError(f"LLM query failed: {e}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @abstractmethod
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data and return results."""
        pass
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Simple logging method."""
        print(f"[{level}] {self.name}: {message}")