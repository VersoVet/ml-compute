"""BoneRotationNet — standalone copy for Ray Serve inference.

EfficientNet-B2 backbone -> (cos theta, sin theta) regression head.
Source: bone-rotation/src/modules/model/rotation_net.py
"""

import math

import timm
import torch
import torch.nn as nn


class BoneRotationNet(nn.Module):
    """Rotation angle predictor using EfficientNet backbone.

    Input: (B, 1, 224, 224) grayscale image
    Output: (B, 2) — [cos(angle), sin(angle)]

    The angle is recovered via atan2(sin, cos).
    """

    def __init__(
        self,
        backbone: str = "efficientnet_b2",
        pretrained: bool = True,
        embed_dim: int = 512,
    ) -> None:
        """Initialize BoneRotationNet.

        Args:
            backbone: timm model name for the encoder.
            pretrained: Whether to use pretrained weights.
            embed_dim: Embedding dimension before rotation head.
        """
        super().__init__()
        self.encoder = timm.create_model(
            backbone,
            pretrained=pretrained,
            in_chans=1,
            num_classes=0,
            global_pool="avg",
        )
        feat_dim: int = self.encoder.num_features

        self.head = nn.Sequential(
            nn.Linear(feat_dim, embed_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(embed_dim, 2),
        )

        nn.init.xavier_uniform_(self.head[-1].weight, gain=0.1)
        nn.init.zeros_(self.head[-1].bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: (B, 1, 224, 224) input images.

        Returns:
            (B, 2) cos/sin predictions.
        """
        features: torch.Tensor = self.encoder(x)
        return self.head(features)

    def get_embedding(self, x: torch.Tensor) -> torch.Tensor:
        """Extract embedding before rotation head.

        Args:
            x: (B, 1, 224, 224) input images.

        Returns:
            (B, embed_dim) feature vectors.
        """
        features: torch.Tensor = self.encoder(x)
        return self.head[0:2](features)

    def predict_angle(self, x: torch.Tensor) -> torch.Tensor:
        """Predict angle in degrees.

        Args:
            x: (B, 1, 224, 224) input images.

        Returns:
            (B,) angles in degrees [0, 360).
        """
        cos_sin = self.forward(x)
        radians = torch.atan2(cos_sin[:, 1], cos_sin[:, 0])
        degrees: torch.Tensor = torch.rad2deg(radians) % 360.0
        return degrees


def angular_error_deg(
    pred: torch.Tensor,
    target: torch.Tensor,
) -> torch.Tensor:
    """Compute angular error in degrees.

    Args:
        pred: (B, 2) predicted [cos, sin].
        target: (B, 2) target [cos, sin].

    Returns:
        (B,) angular error in degrees [0, 180].
    """
    pred_angle = torch.atan2(pred[:, 1], pred[:, 0])
    target_angle = torch.atan2(target[:, 1], target[:, 0])
    diff = pred_angle - target_angle
    diff = (diff + math.pi) % (2 * math.pi) - math.pi
    return torch.abs(diff) * (180.0 / math.pi)
