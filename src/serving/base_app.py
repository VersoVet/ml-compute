"""Base Ray Serve deployment class for ML model inference.

Provides common lifecycle (load, preprocess, predict, postprocess)
and health check. Subclass and implement the three abstract methods.
"""

import logging
import time
from typing import Any

import torch
from ray import serve
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


@serve.deployment(health_check_period_s=30)
class BaseModelDeployment:
    """Base class for Ray Serve model deployments.

    Subclasses must implement _load_model, _preprocess, _postprocess.
    """

    def __init__(self, model_path: str, device: str = "cuda") -> None:
        """Initialize deployment and load model.

        Args:
            model_path: Path to model checkpoint file.
            device: Target device ('cuda' or 'cpu').
        """
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.model = self._load_model(model_path)
        logger.info("Model loaded: %s on %s", model_path, self.device)

    def _load_model(self, path: str) -> torch.nn.Module:
        """Load model from checkpoint. Must be implemented by subclass.

        Args:
            path: Path to model weights.

        Returns:
            Loaded model in eval mode on self.device.
        """
        raise NotImplementedError

    def _preprocess(self, payload: dict[str, Any]) -> torch.Tensor:
        """Convert request payload to input tensor. Must be implemented.

        Args:
            payload: JSON request body.

        Returns:
            Input tensor ready for model forward pass.
        """
        raise NotImplementedError

    def _postprocess(self, output: torch.Tensor, payload: dict[str, Any]) -> dict[str, Any]:
        """Convert model output to response dict. Must be implemented.

        Args:
            output: Raw model output tensor.
            payload: Original request payload (for mode selection etc).

        Returns:
            Response dict to return as JSON.
        """
        raise NotImplementedError

    async def __call__(self, request: Request) -> JSONResponse:
        """Handle inference request.

        Args:
            request: Starlette HTTP request with JSON body.

        Returns:
            JSONResponse with prediction results or error.
        """
        try:
            payload: dict[str, Any] = await request.json()
            t0 = time.perf_counter()

            tensor = self._preprocess(payload)
            with torch.no_grad():
                output = self.model(tensor)

            result = self._postprocess(output, payload)
            result["inference_ms"] = round((time.perf_counter() - t0) * 1000, 1)
            return JSONResponse(result)
        except Exception as e:
            logger.exception("Inference error")
            return JSONResponse({"error": str(e)}, status_code=500)

    def check_health(self) -> None:
        """Ray Serve health check.

        Raises:
            RuntimeError: If model is not loaded.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
