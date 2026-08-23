# Nuclio SAM Proxy

Fonction Nuclio pour proxy des requêtes de segmentation SAM vers le backend ml-compute sur OnyxSoma.

## Architecture

```
CVAT/Client → Nuclio (OnyxSynapse) → ml-compute SAM (OnyxSoma)
              10.0.0.59:9070       10.0.0.44:9469
```

## Déploiement

### Via nuctl CLI

```bash
cd /path/to/nuclio-sam-proxy

# Déployer la fonction
nuctl deploy \
  --project-name ml-compute \
  --function-name sam-proxy \
  --file function.yaml \
  --image-name sam-proxy:v1 \
  --target nuclio

# Ou avec plus d'options
nuctl deploy \
  --project-name ml-compute \
  --function-name sam-proxy \
  --file function.yaml \
  --builder docker \
  --runtime python:3.9 \
  --base-image python:3.9-slim
```

### Via API Nuclio (REST)

```bash
# 1. Créer un archive de la fonction
zip -r sam-proxy.zip model_handler.py requirements.txt function.yaml

# 2. Déployer via API
curl -X POST http://10.0.0.59:8070/api/functions \
  -H "Content-Type: multipart/form-data" \
  -F "function=@sam-proxy.zip" \
  -F "functionConfig=@function.yaml"

# 3. Vérifier le statut
curl http://10.0.0.59:8070/api/functions/ml-compute/sam-proxy

# 4. Tester l'endpoint
curl -X POST http://10.0.0.59:9070/segment \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

## Fichiers

- **model_handler.py** - Handler Nuclio qui forward les requêtes vers ml-compute
- **function.yaml** - Configuration Nuclio (runtime, triggers, resources)
- **requirements.txt** - Dépendances Python (requests, numpy)

## Environnement

| Variable | Valeur | Description |
|----------|--------|-------------|
| `SAM_BACKEND_URL` | `http://10.0.0.44:9469/api/serve/sam/interact` | URL du backend SAM ml-compute |
| `TIMEOUT` | `60.0` | Timeout pour les requêtes backend (secondes) |

## Format Requête

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "points": [[100, 100], [200, 200]],
  "negative_points": null,
  "box": null
}
```

## Format Réponse (Succès)

```json
{
  "status": "success",
  "masks": [[0, 0, 1, 1, ...], ...],
  "iou_predictions": [0.95, 0.87, ...]
}
```

## Format Réponse (Erreur)

```json
{
  "status": "error",
  "detail": "Backend timeout"
}
```

## Tests

### Test unitaire

```bash
python3 -m pytest test_model_handler.py -v
```

### Test d'intégration avec ml-compute

```bash
# 1. Vérifier que SAM est disponible
curl -X GET http://10.0.0.44:9469/api/serve/sam/health

# 2. Tester le proxy
python3 test_proxy.py
```

## Troubleshooting

### Proxy retourne 503 (Cannot connect)
- Vérifier que ml-compute est accessible: `curl http://10.0.0.44:9469/api/serve/sam/health`
- Vérifier que OnyxSynapse peut accéder à OnyxSoma (règles firewall)

### Proxy retourne 504 (Timeout)
- SAM backend trop lent (augmenter TIMEOUT)
- Image SAM pas chargée (vérifier logs de ml-compute)

### Fonction Nuclio ne démarre pas
- Vérifier les logs: `nuctl get logs ml-compute/sam-proxy -p nuclio`
- Vérifier les ressources disponibles sur OnyxSynapse

## Intégration CVAT

Pour utiliser ce proxy comme AI Tool dans CVAT:

1. **Créer une tâche CVAT** avec annotation de type segmentation
2. **Configurer l'AI Tool** :
   - URL: `http://10.0.0.59:9070/segment`
   - Type: `POST`
   - Input format: `application/json`
   - Output format: `application/json`

3. **Utiliser dans l'interface** :
   - Cliquer sur "Run AI Tool" dans la vue annotation
   - L'image est envoyée au proxy
   - Les masques de segmentation s'affichent dans CVAT

## Notes

- Le proxy ne charge pas le modèle SAM localement (économise la mémoire sur OnyxSynapse)
- Toutes les requêtes sont forwardées au backend ml-compute
- La fonction Nuclio est stateless (pas de cache, pas d'état)
