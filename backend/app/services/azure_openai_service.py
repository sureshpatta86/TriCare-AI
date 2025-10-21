"""
Azure OpenAI Service Wrapper

Provides a centralized interface for all Azure OpenAI API interactions with
proper error handling, retry logic, and token management.
"""

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import List, Optional, Dict, Any
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AzureOpenAIService:
    """
    Centralized service for Azure OpenAI interactions.
    
    This service provides methods for chat completions, structured outputs,
    and manages API configuration consistently across the application.
    """
    
    def __init__(self):
        """Initialize Azure OpenAI chat models."""
        self.chat_model = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=settings.azure_openai_deployment_name,
            temperature=0.3,
            max_tokens=2000,
        )
        
        self.vision_model = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=settings.azure_openai_vision_deployment,
            temperature=0.1,  # Very low temperature for consistent medical analysis
            max_tokens=2000,  # Increased for detailed explanations
            model_kwargs={
                "top_p": 0.95,  # More focused sampling
            }
        )
    
    async def generate_completion(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a chat completion from Azure OpenAI.
        
        Args:
            system_prompt: System-level instructions for the model
            user_message: User's input message
            temperature: Optional temperature override (0.0-1.0)
            max_tokens: Optional max tokens override
            
        Returns:
            str: Generated completion text
            
        Raises:
            Exception: If API call fails after retries
        """
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            # Configure model with overrides if provided
            model = self.chat_model
            if temperature is not None:
                model = model.bind(temperature=temperature)
            if max_tokens is not None:
                model = model.bind(max_tokens=max_tokens)
            
            response = await model.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise
    
    async def analyze_with_structured_output(
        self,
        system_prompt: str,
        user_message: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate structured output using Azure OpenAI with JSON mode.
        
        Args:
            system_prompt: System instructions
            user_message: User input
            schema: Expected JSON schema structure
            
        Returns:
            Dict[str, Any]: Parsed structured output
        """
        import json
        
        try:
            # Add JSON formatting instruction to system prompt
            enhanced_prompt = f"""{system_prompt}

You must respond with valid JSON matching this schema:
{schema}

Ensure your response is valid JSON only, with no additional text."""
            
            completion = await self.generate_completion(
                system_prompt=enhanced_prompt,
                user_message=user_message,
                temperature=0.2
            )
            
            # Parse JSON response
            return json.loads(completion)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse structured output: {str(e)}")
            raise ValueError("Failed to generate valid structured output")
        except Exception as e:
            logger.error(f"Error in structured output generation: {str(e)}")
            raise
    
    async def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        image_type: str = "image/png"
    ) -> str:
        """
        Analyze an image using Azure OpenAI Vision model.
        
        Args:
            image_base64: Base64 encoded image
            prompt: Analysis prompt
            image_type: MIME type of image
            
        Returns:
            str: Analysis result
        """
        try:
            messages = [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_type};base64,{image_base64}"
                            }
                        }
                    ]
                )
            ]
            
            response = await self.vision_model.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise


# Singleton instance
_azure_openai_service: Optional[AzureOpenAIService] = None


def get_azure_openai_service() -> AzureOpenAIService:
    """
    Get singleton instance of Azure OpenAI service.
    
    Returns:
        AzureOpenAIService: Shared service instance
    """
    global _azure_openai_service
    if _azure_openai_service is None:
        _azure_openai_service = AzureOpenAIService()
    return _azure_openai_service
