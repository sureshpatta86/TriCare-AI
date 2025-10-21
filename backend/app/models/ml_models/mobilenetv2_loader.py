"""
MobileNetV2 Model Loader for Chest X-ray Classification

Loads and manages the MobileNetV2 model for chest X-ray normal/abnormal classification.
"""

import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import logging
from typing import Optional, Tuple
from pathlib import Path
import io

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MobileNetV2XrayModel:
    """
    MobileNetV2 model for chest X-ray classification.
    
    Classifies chest X-rays as normal or abnormal. Model should be fine-tuned
    on a chest X-ray dataset (e.g., ChestX-ray14, NIH dataset).
    """
    
    def __init__(self):
        """Initialize model and transforms."""
        self.device = torch.device("cuda" if settings.use_gpu and torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = self._get_transforms()
        self.class_names = ["normal", "abnormal"]
        
        logger.info(f"Using device: {self.device}")
    
    def _get_transforms(self):
        """Get image preprocessing transforms."""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def load_model(self, model_path: Optional[str] = None):
        """
        Load the pre-trained model.
        
        Args:
            model_path: Path to model weights file. Uses config default if None.
            
        Raises:
            FileNotFoundError: If model file doesn't exist
        """
        path = Path(model_path or settings.model_path)
        
        if not path.exists():
            raise FileNotFoundError(
                f"Model weights not found at {path}. "
                "Please train or download the model first."
            )
        
        try:
            # Initialize MobileNetV2 architecture
            self.model = models.mobilenet_v2(weights=None)
            
            # Modify final layer for binary classification
            num_features = self.model.classifier[1].in_features
            self.model.classifier[1] = torch.nn.Linear(num_features, 2)
            
            # Load trained weights
            checkpoint = torch.load(path, map_location=self.device)
            
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            else:
                self.model.load_state_dict(checkpoint)
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Model loaded successfully from {path}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
    
    def preprocess_image(self, image_data: bytes) -> torch.Tensor:
        """
        Preprocess image for model input.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            torch.Tensor: Preprocessed image tensor
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply transforms
            image_tensor = self.transform(image)
            
            # Add batch dimension
            image_tensor = image_tensor.unsqueeze(0)
            
            return image_tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise ValueError(f"Failed to preprocess image: {str(e)}")
    
    def predict(self, image_data: bytes) -> Tuple[str, float]:
        """
        Predict class and confidence for X-ray image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Tuple[str, float]: (predicted_class, confidence_score)
            
        Raises:
            RuntimeError: If model not loaded
            ValueError: If image processing fails
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Preprocess image
            image_tensor = self.preprocess_image(image_data)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)
            
            predicted_class = self.class_names[predicted_idx.item()]
            confidence_score = confidence.item()
            
            logger.info(f"Prediction: {predicted_class} (confidence: {confidence_score:.2f})")
            
            return predicted_class, confidence_score
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
    
    def get_feature_map(self, image_data: bytes) -> torch.Tensor:
        """
        Get feature map from model for Grad-CAM visualization.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            torch.Tensor: Feature maps from last convolutional layer
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")
        
        try:
            image_tensor = self.preprocess_image(image_data)
            
            # Get features from last conv layer
            features = []
            def hook(module, input, output):
                features.append(output)
            
            # Register hook on last conv layer
            handle = self.model.features[-1].register_forward_hook(hook)
            
            # Forward pass
            with torch.no_grad():
                _ = self.model(image_tensor)
            
            handle.remove()
            
            return features[0]
            
        except Exception as e:
            logger.error(f"Error getting feature map: {str(e)}")
            raise


# Singleton instance
_model_instance: Optional[MobileNetV2XrayModel] = None


def get_xray_model() -> MobileNetV2XrayModel:
    """
    Get singleton instance of X-ray model.
    
    Returns:
        MobileNetV2XrayModel: Shared model instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = MobileNetV2XrayModel()
        try:
            _model_instance.load_model()
        except FileNotFoundError:
            logger.warning("Model weights not found. Model will not be available for inference.")
    
    return _model_instance
