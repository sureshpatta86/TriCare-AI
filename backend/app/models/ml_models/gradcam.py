"""
Grad-CAM (Gradient-weighted Class Activation Mapping) Implementation

Generates heatmap visualization of model attention for X-ray images.
"""

import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
import io
import base64
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class GradCAM:
    """
    Grad-CAM implementation for visualizing model decisions.
    
    Creates a heatmap showing which regions of the image the model
    focused on when making its prediction.
    """
    
    def __init__(self, model, target_layer):
        """
        Initialize Grad-CAM.
        
        Args:
            model: PyTorch model
            target_layer: Layer to generate CAM from (usually last conv layer)
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self._register_hooks()
    
    def _register_hooks(self):
        """Register forward and backward hooks."""
        def forward_hook(module, input, output):
            self.activations = output.detach()
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()
        
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)
    
    def generate_cam(self, input_tensor: torch.Tensor, target_class: int = None) -> np.ndarray:
        """
        Generate Class Activation Map.
        
        Args:
            input_tensor: Input image tensor (1, C, H, W)
            target_class: Target class index. If None, uses predicted class.
            
        Returns:
            np.ndarray: Heatmap (H, W)
        """
        self.model.eval()
        
        # Forward pass
        output = self.model(input_tensor)
        
        # Get target class
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # Backward pass
        self.model.zero_grad()
        target = output[0, target_class]
        target.backward()
        
        # Get gradients and activations
        gradients = self.gradients.cpu().numpy()[0]  # (C, H, W)
        activations = self.activations.cpu().numpy()[0]  # (C, H, W)
        
        # Calculate weights (global average pooling of gradients)
        weights = np.mean(gradients, axis=(1, 2))  # (C,)
        
        # Weighted combination of activation maps
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        # Apply ReLU
        cam = np.maximum(cam, 0)
        
        # Normalize
        if cam.max() > 0:
            cam = cam / cam.max()
        
        return cam
    
    def overlay_heatmap(
        self,
        original_image: bytes,
        heatmap: np.ndarray,
        alpha: float = 0.4
    ) -> str:
        """
        Overlay heatmap on original image and return as base64.
        
        Args:
            original_image: Original image bytes
            heatmap: Generated heatmap (H, W)
            alpha: Transparency of heatmap overlay
            
        Returns:
            str: Base64 encoded overlaid image
        """
        try:
            # Load original image
            img = Image.open(io.BytesIO(original_image))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_np = np.array(img)
            
            # Resize heatmap to match original image size
            heatmap_resized = cv2.resize(heatmap, (img_np.shape[1], img_np.shape[0]))
            
            # Convert heatmap to RGB
            heatmap_colored = cv2.applyColorMap(
                (heatmap_resized * 255).astype(np.uint8),
                cv2.COLORMAP_JET
            )
            heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
            
            # Overlay
            overlaid = (img_np * (1 - alpha) + heatmap_colored * alpha).astype(np.uint8)
            
            # Convert to base64
            overlaid_img = Image.fromarray(overlaid)
            buffer = io.BytesIO()
            overlaid_img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_base64
            
        except Exception as e:
            logger.error(f"Error overlaying heatmap: {str(e)}")
            raise


def generate_gradcam_heatmap(
    model,
    image_data: bytes,
    target_class: int = None
) -> Tuple[np.ndarray, str]:
    """
    Generate Grad-CAM heatmap for an X-ray image.
    
    Args:
        model: Loaded PyTorch model
        image_data: Raw image bytes
        target_class: Target class for CAM. If None, uses predicted class.
        
    Returns:
        Tuple[np.ndarray, str]: (heatmap, base64_overlaid_image)
    """
    try:
        # Get target layer (last conv layer for MobileNetV2)
        target_layer = model.features[-1]
        
        # Create Grad-CAM instance
        gradcam = GradCAM(model, target_layer)
        
        # Preprocess image
        from app.models.ml_models.mobilenetv2_loader import get_xray_model
        xray_model = get_xray_model()
        input_tensor = xray_model.preprocess_image(image_data)
        
        # Generate CAM
        heatmap = gradcam.generate_cam(input_tensor, target_class)
        
        # Overlay on original image
        overlaid_base64 = gradcam.overlay_heatmap(image_data, heatmap)
        
        return heatmap, overlaid_base64
        
    except Exception as e:
        logger.error(f"Error generating Grad-CAM: {str(e)}")
        raise
