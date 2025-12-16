import os
import openai
from typing import List, Dict, Any

class LLMClient:
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        raise NotImplementedError

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

class VLLMClient(LLMClient):
    def __init__(self, api_url: str = None, model: str = None):
        self.api_url = api_url or os.getenv("VLLM_API_URL", "http://localhost:8000/v1")
        self.model = model or os.getenv("VLLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        # vLLM is OpenAI compatible
        self.client = openai.OpenAI(
            base_url=self.api_url,
            api_key="EMPTY"
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

class GroqClient(LLMClient):
    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.api_key
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # Default behavior
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content
