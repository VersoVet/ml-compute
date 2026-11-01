# bone-train BoneSeg SwinUNETR Ray job

Stable ml-compute entrypoint for the canonical MONAI implementation owned by
`bone-train` (second rideau S3 — hors bone-rotation).

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
`LABEL_GENERATOR_URL`, and the PostgreSQL connection settings. Epochs, batch
size, tiers, learning rate, weight decay, base model and model output directory
are configurable.

## Ontologie = ZONES (pas 11 os legacy)

Classes from label-generator YOLO export (same mapping as bone-ml multitask):

```bash
curl -s "http://10.0.0.59:9466/labels/api/export/yolo?bone_type=humerus" \
  | jq '.class_map | length'
```

`background=0`, zone slugs shifted +1. Resolved inside bone-train
`ontology.fetch_zone_ontology`.

## Gate GOLD — pas de train GPU réel

bone-train refuse `POST /api/boneseg/train` (HTTP 409) tant que
`gold_frames < min_gold_frames` (défaut 50). Ne pas bypasser pour un run GPU
tant que le volume GOLD zones est insuffisant.

## A/B vs bone-ml ResNet-UNet (plus tard)

| | bone-ml | bone-train |
|--|---------|------------|
| Job | `jobs/bone-ml/train_boneseg.py` | `jobs/bone-train/train_boneseg.py` |
| Arch | smp U-Net ResNet50 | MONAI SwinUNETR |
| Métriques | Dice (+ HD95 côté bone-train) | Dice + HD95 |

Quand GOLD ≥ 50 : même `BONE_TYPE`, mêmes tiers, mêmes `test_sets`.
