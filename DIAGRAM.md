# ml-compute - Architecture Diagram

## Nomad + Ray Hybrid Architecture

```mermaid
graph TB
    subgraph Soma["OnyxSoma (10.0.0.44) — Orchestration & Admin"]
        API["FastAPI API<br/>:9469<br/>OnyxClient"]
        RayHead["Ray Head Node<br/>:6380 GCS<br/>:8265 Dashboard<br/>Orchestration Only"]
        NomadHead["Nomad Server<br/>:4646 API<br/>GPU Resource Mgmt<br/>Job Scheduling"]
        API ---|Ray Client| RayHead
        API ---|Nomad API| NomadHead
    end

    subgraph NomadWorkers["Nomad Workers (GPU Orchestration)"]
        Cortex["OnyxCortex (10.0.0.26) ⚡<br/>Nomad Client<br/>GPU: RTX 4070 SUPER 12GB<br/>i7-10700KF 16-core, 46GB RAM<br/>→ SAM via Nomad (exclusive GPU)<br/>→ bone-ml training via Ray"]
        OP["OnyxPoint (10.0.0.86) ⚡<br/>Nomad Client<br/>GPU: T1000 8GB<br/>i5-10400, 32GB RAM<br/>→ Fallback SAM / YOLO training"]
    end

    subgraph RayWorkers["Ray Workers (ML Compute)"]
        Glia["Glia (10.0.0.8) 💾<br/>Ray Worker<br/>CPU: 2x Xeon E5-2630<br/>num_cpus=20, 47GB RAM<br/>→ CPU-only jobs"]
    end

    subgraph Infrastructure["Infrastructure Services"]
        Axon["Axon (10.0.0.21)<br/>Grobid, Ollama, etc."]
    end

    NomadHead -->|nomad client| Cortex
    NomadHead -->|nomad client| OP
    RayHead -->|ray start --address| Cortex
    RayHead -->|ray start --address| Glia

    subgraph Clients["API Clients"]
        Portal["Onyx Portal"]
        BoneML["bone-annotator"]
        BoneRec["bone-recognition"]
    end

    Portal -->|GET /health| API
    Portal -->|POST /api/jobs| API
    Portal -->|POST /api/serve/sam| API
    BoneML -->|POST /api/jobs| API
    BoneRec -->|POST /api/serve/sam| API
```

### GPU Resource Coordination

```mermaid
sequenceDiagram
    actor User
    participant API as ml-compute API
    participant Nomad as Nomad Cluster
    participant SAM as SAM Job
    participant Ray as Ray Cluster
    participant Training as bone-ml Job

    User->>API: POST /api/serve/sam/deploy
    API->>Nomad: Submit sam-inference job
    Nomad->>Cortex: Allocate GPU + schedule
    Cortex->>SAM: Docker container starts
    SAM-->>API: Health check OK
    
    User->>API: POST /api/jobs (bone-ml)
    API->>Nomad: Check GPU availability
    Note over Nomad: GPU locked by SAM
    API-->>User: {"status": "queued", "reason": "GPU occupied by sam"}
    
    User->>API: DELETE /api/serve/sam/undeploy
    API->>Nomad: Stop sam-inference job
    Nomad->>Cortex: Deallocate GPU
    
    API->>Ray: Submit bone-ml job (now GPU free)
    Ray->>Cortex: Schedule on GPU
    Cortex->>Training: Execute training
```

## Module Interactions

```mermaid
graph LR
    Main["FastAPI Main<br/>(main.py)"]
    
    subgraph Modules["Core Modules"]
        Jobs["Jobs Module<br/>Ray Jobs API proxy"]
        Nodes["Nodes Module<br/>Worker monitoring"]
        Serve["Serve Module<br/>Ray Serve management<br/>(deploy/undeploy/status)"]
        Models["Models Module<br/>Registry"]
    end

    subgraph Models_["Data Models"]
        JobReq["JobSubmitRequest"]
        JobRes["JobResponse"]
        NodesRes["NodesResponse"]
        DeployReq["DeployRequest"]
        UndeployReq["UndeployRequest"]
        ServeRes["ServeDeploymentsResponse"]
    end

    RayDash["Ray Dashboard HTTP API<br/>:8265"]

    Main -->|include_router| Jobs
    Main -->|include_router| Nodes
    Main -->|include_router| Serve
    Main -->|include_router| Models

    Jobs -->|service.py| JobReq
    Jobs -->|routes.py| JobRes
    Nodes -->|httpx async| RayDash
    Nodes -->|service.py| NodesRes
    Serve -->|httpx async| RayDash
    Serve -->|routes.py| DeployReq
    Serve -->|routes.py| UndeployReq
    Serve -->|routes.py| ServeRes
```

## Data Flow: Job Submission

```mermaid
sequenceDiagram
    actor Client as Portal/bone-ml
    participant API as FastAPI<br/>:9469
    participant JobsService as jobs/service.py
    participant Ray as Ray Head<br/>:6379
    participant Worker as GPU Worker<br/>(OnyxPoint)

    Client->>API: POST /api/jobs
    Note over API: Parse JobSubmitRequest
    API->>JobsService: submit_job(...)
    JobsService->>Ray: client.submit_job()
    Ray->>Ray: Queue job
    Ray-->>JobsService: job_id
    JobsService-->>API: return job_id
    API-->>Client: 202 Accepted

    Note over Ray,Worker: Job execution
    Ray->>Worker: Assign job
    Worker->>Worker: Execute entrypoint
    Worker-->>Ray: status updates
    Ray-->>JobsService: Webhook (optional)

    Client->>API: GET /api/jobs/{job_id}
    API->>JobsService: get_job_status(job_id)
    JobsService->>Ray: query status + logs
    Ray-->>JobsService: status, logs_tail
    JobsService-->>API: JobResponse
    API-->>Client: 200 OK (status + logs)
```

## Storage Layout

```
/opt/onyx/skills/ml-compute/
├── docker-compose.yml          # Ray head + FastAPI
├── Dockerfile                  # FastAPI image
├── src/                        # Source code
│   ├── main.py                 # FastAPI app
│   ├── models.py               # Pydantic models
│   └── modules/                # 4 core modules
│       ├── jobs/
│       ├── nodes/
│       ├── serve/
│       └── models/
├── config/                     # Ray configuration
│   ├── ray-config.json         # Cluster settings
│   └── workers.json            # Worker registration
├── models/                     # ML models (backup)
│   ├── bone-annotator/         # YOLO models
│   └── bone-recognition/       # EfficientNet models
└── jobs/                       # Job templates Ray
    ├── __init__.py
    ├── bone-annotator/
    │   ├── __init__.py
    │   ├── train_yolo.py          # YOLOv8 training (ultralytics)
    │   └── README.md               # Doc: env vars, exemples curl
    └── bone-recognition/
        ├── __init__.py
        ├── train_efficientnet.py   # EfficientNet-B0 (Phase A+B)
        └── README.md               # Doc: env vars, exemples curl
```

## Deployment Target

- **Host**: OnyxSoma (10.0.0.44)
- **Run Mode**: service (systemd)
- **Containers**: 2 (Ray head, FastAPI wrapper)
- **Networks**: host (direct access to workers)
- **Ports**: 9469 (API), 6379 (Ray), 8265 (Dashboard), 8000 (Serve)
