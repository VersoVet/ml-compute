# Intégration CVAT + SAM via Nuclio Proxy

**Objectif**: Utiliser SAM comme AI Tool dans CVAT pour la segmentation assistée.

**Architecture**:
```
CVAT UI
  ↓ (POST /segment avec image base64)
Nuclio Proxy (10.0.0.59:9070)
  ↓ (Forward à ml-compute)
ml-compute SAM Backend (10.0.0.44:9469)
  ↓
SAM Model (Nomad OnyxCortex)
  ↓
Masques de segmentation
  ↑
CVAT UI (affichage des masques)
```

---

## 1. Prérequis

### Sur OnyxSoma (10.0.0.44) - ml-compute
- ✓ SAM Nomad job running (sam-inference)
- ✓ Endpoint `/api/serve/sam/interact` accessible
- Test: `curl -X GET http://10.0.0.44:9469/api/serve/sam/health`

### Sur OnyxSynapse (10.0.0.59) - Nuclio
- ✓ Service Nuclio installé et running
- ✓ Fonction `sam-proxy` déployée
- Test: `curl -X GET http://10.0.0.59:8070/api/versions`

### Sur OnyxSynapse (10.0.0.59) - CVAT
- ✓ CVAT service running
- Version: CVAT 2.x+
- Test: `curl -X GET http://10.0.0.59:8080/api/server/about`

---

## 2. Configuration de la Fonction Nuclio

### Vérifier le déploiement

```bash
# Lister les fonctions
curl -s http://10.0.0.59:8070/api/functions | jq '.functions[] | {name, state}'

# Détails de sam-proxy
curl -s http://10.0.0.59:8070/api/functions/ml-compute/sam-proxy | jq .
```

### Logs de la fonction

```bash
# Voir les logs
curl -s http://10.0.0.59:8070/api/function_logs/ml-compute/sam-proxy

# Ou via nuctl
nuctl get logs ml-compute/sam-proxy -p nuclio
```

---

## 3. Configuration dans CVAT

### 3.1 Accéder aux paramètres CVAT

1. **Ouvrir CVAT**: http://10.0.0.59:8080
2. **Se connecter** avec un compte admin
3. **Aller à**: Settings → Server Configuration → Plugins

### 3.2 Ajouter l'AI Tool SAM

#### Option A: Via interface CVAT

1. Aller à **Settings → Plugins**
2. Cliquer **+ New Plugin**
3. Remplir les champs:
   ```
   Name: SAM Proxy
   Plugin Type: AI Tool
   Method: POST
   URL: http://10.0.0.59:9070/segment
   Input Format: application/json
   Output Format: application/json
   ```

#### Option B: Via API CVAT

```bash
curl -X POST http://10.0.0.59:8080/api/plugins \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SAM Proxy",
    "type": "ai_tool",
    "method": "POST",
    "url": "http://10.0.0.59:9070/segment",
    "input_format": "application/json",
    "output_format": "application/json"
  }'
```

### 3.3 Configurer les paramètres SAM

Dans CVAT, lors de la création d'une tâche:

1. **Type d'annotation**: Segmentation Instance
2. **AI Tool**: SAM Proxy
3. **Configuration**:
   ```json
   {
     "model": "vit_b",
     "prompt_type": "points",
     "confidence_threshold": 0.5
   }
   ```

---

## 4. Utilisation dans CVAT

### 4.1 Workflow d'annotation

1. **Créer une tâche** dans CVAT
2. **Télécharger les images** à annoter
3. **Ouvrir la vue annotation**
4. **Cliquer sur "AI Tool" → SAM Proxy**
5. **Utiliser le mode segmentation**:
   - **Click positif** (points): Indiquer la région à segmenter
   - **Click négatif** (negative_points): Exclure une région
   - **Bounding box**: (optionnel) Tracer une boîte autour de l'objet

### 4.2 Résultats

- Les masques générés par SAM apparaissent en overlay
- L'utilisateur peut corriger/valider les masques
- Exportable en COCO, Pascal VOC, Yolo, etc.

---

## 5. Format Requête/Réponse

### Requête (CVAT → Nuclio)

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd3PcAAAA...",
  "points": [
    [100, 150],    // positive point (x, y)
    [200, 200]     // another positive point
  ],
  "negative_points": [
    [150, 100]     // negative point to exclude region
  ],
  "box": [50, 50, 300, 300]  // bounding box [x1, y1, x2, y2] (optionnel)
}
```

### Réponse (Nuclio → CVAT)

```json
{
  "status": "success",
  "masks": [
    [0, 0, 1, 1, 0, 0, ...],      // RLE-encoded mask 1
    [0, 1, 1, 0, 1, 1, ...]       // RLE-encoded mask 2
  ],
  "iou_predictions": [0.95, 0.87]  // Confidence scores
}
```

**Erreur**:
```json
{
  "status": "error",
  "detail": "Backend timeout"
}
```

---

## 6. Troubleshooting

### Problème: "AI Tool not responding (503)"

**Cause**: Nuclio proxy ne peut pas atteindre ml-compute

**Solutions**:
1. Vérifier que ml-compute SAM est en cours d'exécution:
   ```bash
   NOMAD_ADDR=http://10.0.0.26:4646 nomad job status sam-inference
   ```

2. Vérifier la connectivité OnyxSynapse → OnyxSoma:
   ```bash
   ssh onyx@10.0.0.59 "curl -X GET http://10.0.0.44:9469/api/serve/sam/health"
   ```

3. Vérifier les logs Nuclio:
   ```bash
   curl -s http://10.0.0.59:8070/api/function_logs/ml-compute/sam-proxy | tail -50
   ```

### Problème: "AI Tool timeout (504)"

**Cause**: SAM backend trop lent (modèle pas chargé, GPU busy)

**Solutions**:
1. Vérifier que le modèle SAM est chargé:
   ```bash
   curl -X GET http://10.0.0.44:9469/api/serve/sam/health
   ```

2. Augmenter le timeout dans le handler:
   ```python
   # model_handler.py
   TIMEOUT = 120.0  # Augmenter à 2 minutes
   ```

3. Vérifier l'usage GPU sur OnyxCortex:
   ```bash
   ssh onyx@10.0.0.26 "nvidia-smi"
   ```

### Problème: "Invalid JSON response"

**Cause**: Format de réponse du backend ne correspond pas

**Solutions**:
1. Tester le endpoint ml-compute directement:
   ```bash
   curl -X POST http://10.0.0.44:9469/api/serve/sam/interact \
     -H "Content-Type: application/json" \
     -d '{"image_base64": "...", "points": [[100, 100]]}'
   ```

2. Vérifier que le proxy forward correctement:
   ```bash
   python3 /home/onyx/projects/skills/ml-compute/jobs/nuclio-sam-proxy/test_proxy.py
   ```

---

## 7. Performance et Optimisation

### Latence Typique

| Opération | Durée |
|-----------|-------|
| Télécharger image (100 MB) | 5-10 ms |
| Forward à Nuclio | 10-20 ms |
| Décoder image + SAM | 2-5 s |
| Encoder réponse | 100-500 ms |
| **Total** | **2-6 secondes** |

### Optimisations Possibles

1. **Cache modèle SAM**: Le modèle est gardé en mémoire GPU (pas de rechargement)
2. **Compression image**: Réduire la taille avant envoi
3. **Batch processing**: Segmenter plusieurs images en parallèle
4. **Model quantization**: Utiliser SAM-H (plus rapide) au lieu de SAM-B

---

## 8. Intégration bone-annotator

### Coordination SAM + bone-annotator

```
bone-annotator UI
  ↓ (Dessiner points de repère)
SAM Proxy (via Nuclio)
  ↓ (Auto-segment os)
bone-ml training
  ↓ (Utiliser masques SAM pour augmentation)
Modèle trained
```

### Configuration

1. **Dans bone-annotator**: Configurer l'endpoint SAM
   ```python
   SAM_ENDPOINT = "http://10.0.0.59:9070/segment"
   ```

2. **Mode annotation**:
   - Marker → SAM segmentation → Valider masque
   - Répéter pour différents os

3. **Export données**:
   - Exporter annotations + masques SAM
   - Importer dans bone-ml pour training

---

## 9. Références

- **CVAT Plugins**: https://opencv.github.io/cvat/docs/manual/advanced/AI%20tools/
- **Nuclio**: https://nuclio.io/docs
- **SAM**: https://github.com/facebookresearch/segment-anything
- **ml-compute**: /home/onyx/projects/skills/ml-compute/API.md
