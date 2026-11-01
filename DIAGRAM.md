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
        NomadServer["Nomad Server<br/>:4646<br/>GPU Allocation"]
        API --- RayHead
        API --- NomadServer
    end

    subgraph Tensor["OnyxTensor (10.0.0.73) — Rig 1 Training"]
        T_3080["GPU 0: RTX 3080 10Go<br/>PCIE1 x16"]
        T_4060["GPU 1: RTX 4060 8Go<br/>riser x1"]
        T_2060["GPU 2: RTX 2060S 8Go<br/>riser x1"]
    end

    subgraph Synth["OnyxSynth (10.0.0.78) — Rig 2 LLM"]
        S_3080["GPU 0: RTX 3080 10Go<br/>PCIE1 x16 (isolee)"]
        S_LLM["GPU 1-6: 6x RTX 2060S<br/>Qwen3-32B-Q8_0<br/>llama.cpp :8080"]
    end

    subgraph Cortex["OnyxCortex (10.0.0.26) — Transitoire"]
        C_4070["RTX 4070S 12Go<br/>SAM + Ray worker"]
    end

    RayHead -->|ray worker| Tensor
    RayHead -->|ray worker| Cortex
    NomadServer -->|GPU alloc| Tensor

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
        TrainingAPI["Training API :9469<br/>Jobs, Nodes, Nomad"]
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
    participant Nomad as Nomad :4646
    participant Ray as Ray Head :6380
    participant Worker as OnyxCortex GPU

    Client->>API: POST /api/jobs
    API->>Nomad: GET /gpu-status
    Note over Nomad: GPU libre ?

    alt GPU occupee
        API-->>Client: 200 (job queued, GPU busy)
    else GPU libre
        API->>Ray: submit_job()
        Ray->>Worker: Schedule on GPU
        Worker->>Worker: Execute training
        Ray-->>API: job_id
        API-->>Client: 202 Accepted
    end

    Client->>API: GET /api/jobs/{id}
    API->>Ray: query status + logs
    Ray-->>API: status, logs
    API-->>Client: 200 OK
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
        Nomad["nomad/<br/>GPU orchestration"]
        GPU["gpu/<br/>acquire / release multi-cible"]
    end

    Main -->|/api/jobs| Jobs
    Main -->|/api/nodes| Nodes
    Main -->|/api/serve| Serve
    Main -->|/api/models| Models
    Main -->|/api/nomad| Nomad
    Main -->|/api/gpu| GPU

    RayDash["Ray Dashboard :8265"]
    NomadAPI["Nomad API :4646"]

    Jobs -->|httpx| RayDash
    Nodes -->|httpx| RayDash
    Serve -->|httpx| RayDash
    Nomad -->|httpx| NomadAPI
    GPU -->|Docker API| CortexDocker["OnyxCortex :2375<br/>SAM + MedSAM2"]

    Config["config.py<br/>ml-compute.yaml"]
    Nomad --- Config
    Main --- Config
```
