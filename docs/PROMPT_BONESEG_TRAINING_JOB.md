# Prompt : Ajout du job d'entraînement BoneSeg dans ml-compute

## Contexte

bone-ml a un nouveau module `boneseg` qui soumet des jobs d'entraînement 
via `POST /api/jobs` avec l'entrypoint `python jobs/bone-ml/train_boneseg.py`.

Ce script doit être créé dans ml-compute pour être exécuté par les workers Ray.

## Fichier à créer

`jobs/bone-ml/train_boneseg.py` — Script Ray pour l'entraînement BoneSegNet.

### Spécifications

**Entrée** (variables d'environnement) :
- `BONE_TYPE` : Type d'os (humerus, femur...)
- `EPOCHS` : Nombre d'époques
- `BATCH_SIZE` : Taille de batch (4 par défaut, limité par 12GB VRAM)
- `IMG_SIZE` : Taille d'image (1408)
- `BASE_MODEL` : Chemin modèle parent pour fine-tuning (vide = from scratch)
- `RUN_ID` : ID du run dans boneseg_training_runs PG
- `RUN_NAME` : Nom du run (ex: humerus_boneseg_gen3)
- `TIERS` : Tiers à utiliser, séparés par virgule (gold,silver)
- `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASSWORD` : PostgreSQL
- `LEARNING_RATE`, `WEIGHT_DECAY` : Hyperparamètres
- `ML_MODELS_DIR` : Répertoire de sortie (/mnt/ml-store/models)

**Pipeline** :
1. Charger les annotations depuis PostgreSQL (schema bone_annotations)
2. Charger les images depuis `/mnt/bonestore` (NFS monté sur le worker)
3. Split train/val 80/20
4. Créer BoneSegNet (smp U-Net + MC-Dropout, encoder ResNet50)
5. Entraîner avec TierWeightedSegLoss (CE + Dice, poids par tier)
6. Optimizer: AdamW, scheduler: CosineAnnealingWarmRestarts
7. Mixed precision (torch.amp)
8. Early stopping (patience 15 epochs)
9. Sauver le best model dans `{ML_MODELS_DIR}/{RUN_NAME}_best.pt`
10. Mettre à jour PG : boneseg_training_runs avec best_dice, per_class_dice

**Checkpoint format** :
```python
torch.save({
    "model_state_dict": model.state_dict(),
    "n_classes": n_classes,
    "encoder_name": "resnet50",
    "bone_classes": bone_class_map,
    "generation": generation,
    "best_dice": best_dice,
    "per_class_dice": per_class_dice,
}, model_path)
```

**Dependencies** (injectées dans runtime_env.pip) :
- segmentation-models-pytorch, timm, blosc2, Pillow, httpx, asyncpg, psutil, pyyaml

**Contrainte GPU** :
- Une seule RTX 4070 Super 12GB disponible
- Batch size 4 max avec images 1408x1408
- `num_gpus: 1` dans submit_kwargs → Ray queue naturellement si GPU occupée

### Pattern à suivre

Voir `jobs/bone-ml/train_multitask.py` existant pour le pattern :
- Chargement PG synchrone (asyncpg en mode sync ou asyncio.run)
- Boucle d'entraînement PyTorch standard
- Logging des métriques par époque
- Sauvegarde best model sur NFS
- Update PG à la fin (status, metrics)

### NFS requis sur le worker

Le worker Ray doit avoir ces volumes montés (déjà configuré dans docker-compose) :
- `/mnt/ml-store:/mnt/ml-store:rw` — modèles et runs
- `/mnt/bonestore:/mnt/bonestore:ro` — images source
