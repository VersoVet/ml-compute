"""Ray Serve deployment for Segment Anything Model (SAM).

IMPORTANT: SAM is deployed as a stateful Ray Serve actor with GPU reservation.
When active, it reserves num_gpus=1 on OnyxCortex, blocking other GPU jobs.

Usage strategy:
1. Start SAM when annotations begin: POST /serve/start-sam
2. Use for annotations: POST /api/interact
3. Stop SAM when done: POST /serve/stop-sam
4. Launch training jobs (GPU now available): POST /api/jobs

Never use num_gpus=0.5 for SAM - GPU sharing risks CUDA OOM.
Never deploy on OnyxPoint (T1000 8GB is insufficient for vit_b ~10GB).
"""

import io
import logging
import os
from typing import Any

from ray import serve

logger = logging.getLogger(__name__)


@serve.deployment(
    name="sam-vit-b",
    ray_actor_options={
        "num_gpus": 1,
        "memory": 2_000_000_000,
    },
)
class SAMDeployment:
    """SAM (Segment Anything Model) deployment for interactive segmentation."""

    def __init__(self):
        """Initialize SAM model on GPU."""
        # Lazy imports (only when Ray Serve deploys this actor)
        import cv2
        import numpy as np
        from PIL import Image
        from segment_anything import SamPredictor, sam_model_registry

        model_path = os.path.expanduser("~/sam-gpu/sam_vit_b_01ec64.pth")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"SAM model not found at {model_path}")

        logger.info(f"Loading SAM model from {model_path}")
        self.device = "cuda"

        # Load SAM model
        sam = sam_model_registry["vit_b"](checkpoint=model_path)
        sam.to(device=self.device)

        self.predictor = SamPredictor(sam)
        logger.info("✓ SAM model loaded successfully on GPU")

    async def interact(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Interactive segmentation endpoint.

        Args:
            payload: Dict with:
                - image: base64-encoded image or numpy array
                - positive_points: list of [x, y] coordinates for foreground
                - negative_points: list of [x, y] coordinates for background
                - prompt_labels: optional, defaults to 1s for positive, 0s for negative

        Returns:
            Dict with:
                - mask: base64-encoded binary mask (H, W)
                - area: pixel count of mask
                - low_res_logits: low resolution logits for refinement
        """
        try:
            import base64
            import cv2
            import numpy as np
            from PIL import Image

            # Decode image
            image_data = payload.get("image")
            if isinstance(image_data, str):
                # base64 string
                image_bytes = base64.b64decode(image_data)
                image = np.array(Image.open(io.BytesIO(image_bytes)))
            else:
                image = np.array(image_data)

            # Handle grayscale → RGB
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

            # Set image for predictor
            self.predictor.set_image(image)

            # Parse points
            positive_points = payload.get("positive_points", [])
            negative_points = payload.get("negative_points", [])

            # Build input points and labels
            input_points = []
            input_labels = []

            for pt in positive_points:
                input_points.append([pt[0], pt[1]])
                input_labels.append(1)

            for pt in negative_points:
                input_points.append([pt[0], pt[1]])
                input_labels.append(0)

            # Convert to numpy
            input_points = np.array(input_points) if input_points else None
            input_labels = np.array(input_labels) if input_labels else None

            # Predict
            if input_points is not None:
                masks, scores, logits = self.predictor.predict(
                    point_coords=input_points,
                    point_labels=input_labels,
                    multimask_output=True,
                )

                # Use best mask (highest score)
                mask = masks[np.argmax(scores)]
            else:
                logger.warning("No points provided for segmentation")
                mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

            # Encode mask as base64
            import base64
            import numpy as np

            mask_uint8 = (mask * 255).astype(np.uint8)
            _, encoded = cv2.imencode(".png", mask_uint8)
            mask_base64 = base64.b64encode(encoded).decode("utf-8")

            return {
                "mask": mask_base64,
                "area": int(np.sum(mask)),
                "status": "success",
                "image_shape": image.shape,
            }

        except Exception as e:
            logger.error(f"SAM prediction failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def __call__(self, request):
        """HTTP handler for Ray Serve."""
        from starlette.responses import JSONResponse

        if request.method == "POST":
            payload = await request.json()
            result = await self.interact(payload)
            return JSONResponse(result)
        else:
            return JSONResponse({"error": "Use POST method"}, status_code=400)
