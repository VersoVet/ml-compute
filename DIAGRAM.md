# ml-compute - Architecture Diagram

## Multi-Backend Compute

```mermaid
graph LR
    subgraph Clients["Skills Clients"]
        BoneML["bone-ml"]
        BoneAnn["bone-annotator"]
        BoneRec["bone-recognition"]
    end

    subgraph mlcompute["ml-compute API :9469"]
        Router["BackendManager<br/>auto-select"]
    end

    subgraph Backends["Compute Backends"]
        Local["Local Ray Cluster (actuel)<br/>RTX 4070 SUPER 12GB<br/>OnyxCortex"]
        Lightning["Lightning AI<br/>Tesla T4 16GB<br/>~22h GPU/mois"]
        Kaggle["Kaggle Notebooks<br/>Tesla T4 16GB<br/>30h GPU/semaine"]
    end

    BoneML -->|POST /api/compute/submit| Router
    BoneAnn -->|POST /api/compute/submit| Router
    BoneRec -->|POST /api/compute/submit| Router

    Router -->|backend: local| Local
    Router -->|backend: lightning| Lightning
    Router -->|backend: kaggle| Kaggle

    style Local fill:#3498db,color:#fff
    style Lightning fill:#9b59b6,color:#fff
    style Kaggle fill:#2ecc71,color:#fff
```

---

## Cluster Ray + Rigs GPU

```mermaid
graph TB
    subgraph Soma["OnyxSoma (10.0.0.44) — Orchestration"]
        API["ml-compute API<br/>:9469"]
        RayHead["Ray Head<br/>:6380 GCS<br/>:8265 Dashboard"]
        GPUAlloc["gpu_allocator<br/>PostgreSQL slots<br/>FIFO queue"]
        API --- RayHead
        API --- GPUAlloc
    end

    subgraph Tensor["OnyxTensor (10.0.0.73) — Rig 1 Training (priorité 2)"]
        T_3080["GPU 0: RTX 3080 10Go<br/>PCIE1 x16"]
        T_4060["GPU 1: RTX 4060 8Go<br/>riser x1"]
        T_2060["GPU 2: RTX 2060S 8Go<br/>riser x1"]
    end

    subgraph Synth["OnyxSynth (10.0.0.78) — Rig 2 LLM"]
        S_3080["GPU 0: RTX 3080 10Go<br/>PCIE1 x16 (isolee)"]
        S_LLM["GPU 1-6: 6x RTX 2060S<br/>Qwen3-32B-Q8_0<br/>llama.cpp :8080"]
    end

    subgraph Cortex["OnyxCortex (10.0.0.26) — Bone Training Primary (priorité 1)"]
        C_4070["RTX 4070S 12Go<br/>100% training<br/>/data/ml/"]
    end

    RayHead -->|ray worker| Tensor
    RayHead -->|ray worker GPU 0| S_3080
    RayHead -->|ray worker| Cortex
    GPUAlloc -->|slot exclusif| Cortex
    GPUAlloc -->|slot exclusif| Tensor

    subgraph Storage["NFS Storage"]
        MLStore["/mnt/ml-store"]
        BoneStore["/mnt/bonestore"]
    end

    Tensor --- MLStore
    Cortex --- MLStore
    Cortex --- BoneStore

    subgraph Clients["Skills Clients"]
        BoneML["bone-ml"]
        PaperReader["paper-reader"]
        LabelGen["label-generator"]
    end

    BoneML -->|POST /api/jobs| API
    PaperReader -->|chat/completions| S_LLM
    LabelGen -->|chat/completions| S_LLM

    style S_LLM fill:#2ecc71,color:#fff
    style T_3080 fill:#3498db,color:#fff
    style C_4070 fill:#e67e22,color:#fff
```

## BoneSeg Training Flow (A/B)

```mermaid
sequenceDiagram
    actor BoneML as bone-ml :9463
    actor BoneTrain as bone-train :8210
    participant API as ml-compute :9469
    participant Ray as Ray Head
    participant Worker as OnyxCortex GPU
    participant PG as PostgreSQL bone_annotations

    Note over BoneML,BoneTrain: A/B : meme ontologie ZONES, memes test_sets

    BoneML->>PG: register_training_run
    BoneML->>API: POST /api/jobs train_boneseg.py (ResNet50)
    API->>Ray: submit job num_gpus=1
    Ray->>Worker: train BoneSegNet smp U-Net
    Worker->>PG: load GOLD annotations
    Worker->>Worker: train early stopping
    Worker->>PG: update best_dice metrics
    Worker-->>Ray: SUCCEEDED

    BoneTrain->>PG: register_training_run
    BoneTrain->>API: POST /api/jobs train_boneseg.py (SwinUNETR)
    API->>Ray: submit job num_gpus=1
    Ray->>Worker: train MONAI SwinUNETR
    Worker->>PG: load GOLD annotations
    Worker->>Worker: train + HD95
    Worker->>PG: update best_dice metrics
    Worker-->>Ray: SUCCEEDED
```

## Separation SAM / ml-compute

```mermaid
graph LR
    subgraph mlcompute["ml-compute (OnyxSoma)"]
        TrainingAPI["Training API :9469<br/>Jobs, Nodes, GPU Allocator"]
    end

    subgraph boneannotator["bone-annotator (OnyxSynapse)"]
        BA_API["bone-annotator API<br/>:9464"]
    end

    subgraph cortex["OnyxCortex (10.0.0.26)"]
        SAM["SAM/MedSAM Docker<br/>:9470<br/>GPU direct"]
        RayWorker["Ray Worker<br/>Training jobs"]
    end

    subgraph cvat["CVAT (OnyxSynapse)"]
        CVAT_UI["CVAT UI"]
        Nuclio["Nuclio Functions"]
    end

    CVAT_UI -->|annotation| Nuclio
    Nuclio -->|segmentation| SAM
    BA_API -->|start/stop| SAM

    TrainingAPI -->|submit job| RayWorker

    SAM -.->|GPU exclusive| RayWorker

    style SAM fill:#e74c3c,color:#fff
    style RayWorker fill:#3498db,color:#fff
```

**Point cle** : SAM et Ray Worker partagent le meme GPU sur OnyxCortex.
L'API `POST /api/gpu/acquire` stoppe SAM et MedSAM2 avant un training, puis
`POST /api/gpu/release` les relance.

**Protocole CVAT** : Nuclio appelle `POST http://10.0.0.26:9470/api/embed` qui doit
retourner `{blob, shape}` (image `sam-inference`, gere par bone-annotator).

## Job Submission Flow

```mermaid
sequenceDiagram
    actor Client as bone-ml / bone-annotator
    participant API as ml-compute :9469
    participant Alloc as gpu_allocator<br/>PostgreSQL
    participant Queue as FIFO queue<br/>gpu_job_queue
    participant Ray as Ray Head :6380
    participant Worker as OnyxCortex (p1) / Tensor (p2)

    Client->>API: POST /api/jobs
    API->>Alloc: tenter slot libre (priorité 1 → Cortex, 2 → Tensor)
    Note over Alloc: GPU libre ?

    alt GPU occupee (tous les slots busy)
        Alloc->>Queue: enqueue job (FIFO)
        API-->>Client: 202 QUEUED (queue_id, position)
        Note over Queue: background worker poll 10s
        Queue->>Alloc: slot libéré → dispatch
        Alloc->>Ray: submit_job()
    else GPU libre
        Alloc->>Alloc: acquire slot (atomic)
        API->>Ray: submit_job()
        Ray->>Worker: Schedule on GPU
        Worker->>Worker: Execute training
        Ray-->>API: job_id
        API-->>Client: 202 SUBMITTED (job_id)
    end

    Worker-->>Ray: SUCCEEDED / FAILED
    Ray-->>Alloc: background worker detecte fin
    Alloc->>Alloc: release slot → dispatch queue suivant

    Client->>API: GET /api/jobs/{id}
    API->>Ray: query status + logs
    Ray-->>API: status, logs
    API-->>Client: 200 OK
```

## Ray Serve Inference Flow

```mermaid
sequenceDiagram
    actor Client as skill client
    participant API as ml-compute :9469
    participant Serve as Ray Serve :8000
    participant App as bone_rotation_app / base_app
    participant GPU as OnyxCortex GPU

    Client->>API: POST /api/serve/predict/{app_name}
    API->>Serve: forward request
    Serve->>App: route to replica
    App->>GPU: inference (PyTorch)
    GPU-->>App: result tensor
    App-->>Serve: prediction + confidence
    Serve-->>API: response
    API-->>Client: 200 {result, duration_ms}

    Client->>API: GET /api/serve/deployments/{name}/status
    API->>Serve: GET /api/applications
    Serve-->>API: status, replicas, GPU
    API-->>Client: 200 {status, num_replicas}
```

## Module Interactions

```mermaid
graph LR
    Main["main.py<br/>FastAPI"]

    subgraph Modules
        Jobs["jobs/<br/>Ray Jobs proxy"]
        Nodes["nodes/<br/>Worker monitoring"]
        Serve["serve/<br/>Ray Serve mgmt"]
        Models["models/<br/>Model registry"]
        GPUAlloc["gpu_allocator/<br/>PostgreSQL slots + FIFO queue"]
        GPU["gpu/<br/>acquire / release multi-cible"]
        Serving["serving/<br/>Ray Serve apps (inference)"]
    end

    Main -->|/api/jobs| Jobs
    Main -->|/api/nodes| Nodes
    Main -->|/api/serve| Serve
    Main -->|/api/models| Models
    Main -->|/api/gpu-allocator| GPUAlloc
    Main -->|/api/gpu| GPU
    Main -->|/api/serve/predict| Serving

    RayDash["Ray Dashboard :8265"]
    PG["PostgreSQL<br/>gpu_slots, gpu_job_queue"]

    Jobs -->|httpx| RayDash
    Nodes -->|httpx| RayDash
    Serve -->|httpx| RayDash
    Serving -->|Ray Serve SDK| RayDash
    GPUAlloc -->|asyncpg| PG
    Jobs -->|via allocator| GPUAlloc
    GPU -->|Docker API| CortexDocker["OnyxCortex :2375<br/>SAM + MedSAM2"]

    Config["config.py<br/>ml-compute.yaml"]
    GPUAlloc --- Config
    Main --- Config
```
