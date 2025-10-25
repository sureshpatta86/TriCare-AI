"""
Unit tests for Azure OpenAI Service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import json

from app.services.azure_openai_service import AzureOpenAIService, get_azure_openai_service


class TestAzureOpenAIServiceInitialization:
    """Test service initialization"""
    
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    def test_service_initializes_chat_model(self, mock_azure_chat):
        """Test that chat model is initialized correctly"""
        service = AzureOpenAIService()
        
        assert mock_azure_chat.called
        assert service.chat_model is not None
    
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    def test_service_initializes_vision_model(self, mock_azure_chat):
        """Test that vision model is initialized correctly"""
        service = AzureOpenAIService()
        
        assert service.vision_model is not None
    
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    def test_get_singleton_instance(self, mock_azure_chat):
        """Test that get_azure_openai_service returns singleton"""
        # Reset singleton
        import app.services.azure_openai_service as service_module
        service_module._azure_openai_service = None
        
        service1 = get_azure_openai_service()
        service2 = get_azure_openai_service()
        
        assert service1 is service2


class TestGenerateCompletion:
    """Test completion generation"""
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_generate_completion_success(self, mock_azure_chat):
        """Test successful completion generation"""
        # Mock response
        mock_response = Mock()
        mock_response.content = "This is a test response"
        
        mock_model = Mock()
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_azure_chat.return_value = mock_model
        
        service = AzureOpenAIService()
        service.chat_model = mock_model
        
        result = await service.generate_completion(
            system_prompt="You are a helpful assistant",
            user_message="Hello, how are you?"
        )
        
        assert result == "This is a test response"
        assert mock_model.ainvoke.called
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_generate_completion_with_custom_temperature(self, mock_azure_chat):
        """Test completion with custom temperature"""
        mock_response = Mock()
        mock_response.content = "Response"
        
        mock_model = Mock()
        mock_model.bind = Mock(return_value=mock_model)
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_azure_chat.return_value = mock_model
        
        service = AzureOpenAIService()
        service.chat_model = mock_model
        
        result = await service.generate_completion(
            system_prompt="System prompt",
            user_message="User message",
            temperature=0.7
        )
        
        assert result == "Response"
        mock_model.bind.assert_called_with(temperature=0.7)
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_generate_completion_with_max_tokens(self, mock_azure_chat):
        """Test completion with custom max tokens"""
        mock_response = Mock()
        mock_response.content = "Response"
        
        mock_model = Mock()
        mock_model.bind = Mock(return_value=mock_model)
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_azure_chat.return_value = mock_model
        
        service = AzureOpenAIService()
        service.chat_model = mock_model
        
        result = await service.generate_completion(
            system_prompt="System prompt",
            user_message="User message",
            max_tokens=1000
        )
        
        assert result == "Response"
        mock_model.bind.assert_called_with(max_tokens=1000)
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_generate_completion_error_handling(self, mock_azure_chat):
        """Test error handling in completion generation"""
        mock_model = Mock()
        mock_model.ainvoke = AsyncMock(side_effect=Exception("API Error"))
        mock_azure_chat.return_value = mock_model
        
        service = AzureOpenAIService()
        service.chat_model = mock_model
        
        with pytest.raises(Exception) as exc_info:
            await service.generate_completion(
                system_prompt="System prompt",
                user_message="User message"
            )
        
        assert "API Error" in str(exc_info.value)


class TestStructuredOutput:
    """Test structured output generation"""
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_structured_output_success(self, mock_azure_chat):
        """Test successful structured output generation"""
        expected_output = {
            "urgency": "high",
            "symptoms": ["fever", "cough"],
            "recommendation": "See a doctor"
        }
        
        mock_response = Mock()
        mock_response.content = json.dumps(expected_output)
        
        mock_model = Mock()
        mock_model.bind = Mock(return_value=mock_model)
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_azure_chat.return_value = mock_model
        
        service = AzureOpenAIService()
        service.chat_model = mock_model
        
        schema = {
            "urgency": "string",
            "symptoms": "list",
            "recommendation": "string"
        }
        
        result = await service.analyze_with_structured_output(
            system_prompt="Analyze symptoms",
            user_message="Patient has fever and cough",
            schema=schema
        )
        
        assert result == expected_output
        assert result["urgency"] == "high"
        assert len(result["symptoms"]) == 2
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_structured_output_invalid_json(self, mock_azure_chat):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.content = "This is not valid JSON"
        
        mock_model = Mock()
        mock_model.bind = Mock(return_value=mock_model)
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_azure_chat.return_value = mock_model
        
        service = AzureOpenAIService()
        service.chat_model = mock_model
        
        schema = {"field": "type"}
        
        with pytest.raises(ValueError) as exc_info:
            await service.analyze_with_structured_output(
                system_prompt="System",
                user_message="Message",
                schema=schema
            )
        
        assert "valid structured output" in str(exc_info.value).lower()


class TestImageAnalysis:
    """Test image analysis functionality"""
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_analyze_image_success(self, mock_azure_chat):
        """Test successful image analysis"""
        mock_response = Mock()
        mock_response.content = "This X-ray shows normal lung structure"
        
        mock_vision_model = Mock()
        mock_vision_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_azure_chat.return_value = mock_vision_model
        
        service = AzureOpenAIService()
        service.vision_model = mock_vision_model
        
        result = await service.analyze_image(
            image_base64="base64encodedstring",
            prompt="Analyze this X-ray image",
            image_type="image/png"
        )
        
        assert result == "This X-ray shows normal lung structure"
        assert mock_vision_model.ainvoke.called
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_analyze_image_different_format(self, mock_azure_chat):
        """Test image analysis with different image format"""
        mock_response = Mock()
        mock_response.content = "Analysis result"
        
        mock_vision_model = Mock()
        mock_vision_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_azure_chat.return_value = mock_vision_model
        
        service = AzureOpenAIService()
        service.vision_model = mock_vision_model
        
        result = await service.analyze_image(
            image_base64="base64string",
            prompt="Analyze this image",
            image_type="image/jpeg"
        )
        
        assert result == "Analysis result"
        
        # Verify the image URL was constructed correctly
        call_args = mock_vision_model.ainvoke.call_args
        messages = call_args[0][0]
        image_content = messages[0].content[1]
        assert "image/jpeg" in image_content["image_url"]["url"]
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_analyze_image_error_handling(self, mock_azure_chat):
        """Test error handling in image analysis"""
        mock_vision_model = Mock()
        mock_vision_model.ainvoke = AsyncMock(side_effect=Exception("Vision API Error"))
        mock_azure_chat.return_value = mock_vision_model
        
        service = AzureOpenAIService()
        service.vision_model = mock_vision_model
        
        with pytest.raises(Exception) as exc_info:
            await service.analyze_image(
                image_base64="base64string",
                prompt="Analyze",
                image_type="image/png"
            )
        
        assert "Vision API Error" in str(exc_info.value)


class TestMessageConstruction:
    """Test proper message construction for API calls"""
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_completion_messages_structure(self, mock_azure_chat):
        """Test that messages are structured correctly for completion"""
        mock_response = Mock()
        mock_response.content = "Response"
        
        mock_model = Mock()
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_azure_chat.return_value = mock_model
        
        service = AzureOpenAIService()
        service.chat_model = mock_model
        
        await service.generate_completion(
            system_prompt="System instruction",
            user_message="User question"
        )
        
        # Verify messages structure
        call_args = mock_model.ainvoke.call_args
        messages = call_args[0][0]
        
        assert len(messages) == 2
        assert messages[0].content == "System instruction"
        assert messages[1].content == "User question"
    
    @pytest.mark.asyncio
    @patch('app.services.azure_openai_service.AzureChatOpenAI')
    async def test_image_analysis_messages_structure(self, mock_azure_chat):
        """Test that image analysis messages include both text and image"""
        mock_response = Mock()
        mock_response.content = "Analysis"
        
        mock_vision_model = Mock()
        mock_vision_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_azure_chat.return_value = mock_vision_model
        
        service = AzureOpenAIService()
        service.vision_model = mock_vision_model
        
        await service.analyze_image(
            image_base64="testbase64",
            prompt="Test prompt",
            image_type="image/png"
        )
        
        # Verify message structure
        call_args = mock_vision_model.ainvoke.call_args
        messages = call_args[0][0]
        
        assert len(messages) == 1
        message_content = messages[0].content
        assert len(message_content) == 2
        assert message_content[0]["type"] == "text"
        assert message_content[1]["type"] == "image_url"
        assert "data:image/png;base64,testbase64" in message_content[1]["image_url"]["url"]
