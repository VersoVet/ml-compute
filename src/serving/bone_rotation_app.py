"""Ray Serve deployment for bone-rotation inference.

EfficientNet-B2 angle regression (0-360 degrees).
Accepts base64-encoded grayscale bone images, returns angle predictions
or 512-dim embeddings.
"""

import base64
import io
import logging
from typing import Any

import torch
from PIL import Image
from ray import serve

from src.serving.base_app import BaseModelDeployment
from src.serving.models.rotation_net import BoneRotationNet

logger = logging.getLogger(__name__)

IMG_SIZE = 224
NORMALIZE_MEAN = 0.485
NORMALIZE_STD = 0.229
MAX_BATCH = 32


def _decode_image(b64: str, device: torch.device) -> torch.Tensor:
    """Decode a base64 image to a normalized (1, 1, 224, 224) tensor.

    Args:
        b64: Base64-encoded image bytes (any PIL-supported format).
        device: Target torch device.

    Returns:
        Tensor of shape (1, 1, 224, 224), float32, normalized.
    """
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("L").resize((IMG_SIZE, IMG_SIZE))
    arr = torch.frombuffer(bytearray(img.tobytes()), dtype=torch.uint8)
    tensor = arr.float().div(255.0).reshape(1, 1, IMG_SIZE, IMG_SIZE)
    tensor = (tensor - NORMALIZE_MEAN) / NORMALIZE_STD
    return tensor.to(device)


@serve.deployment(
    health_check_period_s=30,
    ray_actor_options={"num_gpus": 1},
)
class BoneRotationDeployment(BaseModelDeployment):
    """Bone rotation angle inference deployment.

    Modes:
        - 'predict' (default): returns angle_deg (0-360) and confidence.
        - 'embedding': returns 512-dim feature vector.

    Supports single image or batch (up to 32).
    """

    def _load_model(self, path: str) -> torch.nn.Module:
        """Load BoneRotationNet from checkpoint.

        Args:
            path: Path to .pt checkpoint file.

        Returns:
            BoneRotationNet in eval mode on self.device.
        """
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        state_dict = checkpoint.get("model_state_dict", checkpoint)

        model = BoneRotationNet(pretrained=False)
        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()
        logger.info("BoneRotationNet loaded from %s", path)
        return model

    def _preprocess(self, payload: dict[str, Any]) -> torch.Tensor:
        """Convert payload to batched input tensor.

        Args:
            payload: Must contain 'image' (str) or 'images' (list[str]),
                     each being a base64-encoded image.

        Returns:
            Tensor of shape (B, 1, 224, 224).

        Raises:
            ValueError: If no image provided or batch exceeds MAX_BATCH.
        """
        images_b64: list[str] = payload.get("images", [])
        single = payload.get("image")
        if single and not images_b64:
            images_b64 = [single]

        if not images_b64:
            raise ValueError("Provide 'image' (str) or 'images' (list[str])")
        if len(images_b64) > MAX_BATCH:
            raise ValueError(f"Batch size {len(images_b64)} exceeds max {MAX_BATCH}")

        tensors = [_decode_image(b64, self.device) for b64 in images_b64]
        return torch.cat(tensors, dim=0)

    def _postprocess(self, output: torch.Tensor, payload: dict[str, Any]) -> dict[str, Any]:
        """Convert model output to response dict.

        Args:
            output: (B, 2) cos/sin predictions from the model.
            payload: Original request — uses 'mode' key.

        Returns:
            Dict with predictions list, each containing angle_deg
            and confidence (predict mode) or embedding (embedding mode).
        """
        mode: str = payload.get("mode", "predict")

        if mode == "embedding":
            # Re-run through embedding path
            tensor = self._preprocess(payload)
            embeddings = self.model.get_embedding(tensor)
            return {
                "predictions": [{"embedding": emb.cpu().tolist()} for emb in embeddings],
            }

        # Default: angle prediction
        cos_vals = output[:, 0]
        sin_vals = output[:, 1]
        angles_rad = torch.atan2(sin_vals, cos_vals)
        angles_deg = (torch.rad2deg(angles_rad) % 360.0).cpu().tolist()
        norms = torch.sqrt(cos_vals**2 + sin_vals**2).cpu().tolist()

        predictions = [
            {
                "angle_deg": round(angle, 2),
                "confidence": round(min(float(norm), 1.0), 4),
                "cos": round(float(cos_vals[i]), 6),
                "sin": round(float(sin_vals[i]), 6),
            }
            for i, (angle, norm) in enumerate(zip(angles_deg, norms))
        ]

        return {"predictions": predictions}


def build_app(model_path: str = "/mnt/ml-store/models/bone-rotation/best.pt") -> serve.Application:
    """Build the Ray Serve application.

    Args:
        model_path: Default model path (overridden by deploy_model init_args).

    Returns:
        Ray Serve Application handle.
    """
    return BoneRotationDeployment.bind(model_path=model_path)


app = build_app()
