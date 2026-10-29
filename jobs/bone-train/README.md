# bone-train BoneSeg SwinUNETR Ray job

Stable ml-compute entrypoint for the canonical MONAI implementation owned by
`bone-train`.

## Ray paths

- Entrypoint: `python jobs/bone-train/train_boneseg.py`
- Working directory: `/opt/onyx/skills/ml-compute`
- Python module source: `/opt/onyx/skills/bone-train`

The submitting `runtime_env` must include both:

```json
{
  "working_dir": "/opt/onyx/skills/ml-compute",
  "py_modules": ["/opt/onyx/skills/bone-train"]
}
```

Ray uploads these paths from OnyxSoma and makes them available to the driver on
OnyxCortex. The wrapper locates the uploaded `bone-train` root and runs its
canonical `jobs/train_boneseg.py`, which trains `BoneSegModel` (MONAI
SwinUNETR).

Required environment variables are supplied by `bone-train`'s
`src/modules/boneseg/train_service.py`: `BONE_TYPE`, `RUN_NAME`, `PG_PASSWORD`,
and the PostgreSQL connection settings. Epochs, batch size, tiers, learning
rate, weight decay, base model and model output directory are configurable.
