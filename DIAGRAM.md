# ml-compute - Architecture Diagram

## Ray Cluster Architecture

```mermaid
graph TB
    subgraph Soma["OnyxSoma (10.0.0.44)"]
        API["FastAPI Wrapper<br/>:9469<br/>OnyxClient"]
        RayHead["Ray Head Node<br/>:6379 GCS<br/>:8265 Dashboard<br/>:8000 Serve"]
        API ---|Ray Client| RayHead
    end

    subgraph Workers["Workers (External)"]
        OP["OnyxPoint (10.0.0.86)<br/>GPU: T1000 8GB<br/>num_gpus=1<br/>YOLO/PyTorch"]
        Glia["Glia<br/>CPU Worker<br/>num_cpus=8<br/>Preprocessing"]
        Axon["Axon (10.0.0.21)<br/>CPU Worker<br/>num_cpus=4<br/>Grobid/Text"]
    end

    RayHead -->|ray start --address| OP
    RayHead -->|ray start --address| Glia
    RayHead -->|ray start --address| Axon

    subgraph Client["Clients"]
        Portal["Onyx Portal<br/>(Dashboard)"]
        BoneML["bone-annotator<br/>(Training jobs)"]
        BoneRec["bone-recognition<br/>(Inference)"]
    end

    Portal -->|GET /health| API
    Portal -->|POST /api/jobs| API
    Portal -->|GET /api/nodes| API
    BoneML -->|POST /api/jobs| API
    BoneRec -->|POST /api/serve| API
    Portal -->|GET /api/serve/status| API
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
└── jobs/                       # Job templates
    ├── bone-annotator/
    │   ├── train_yolo.py
    │   └── predict_batch.py
    └── bone-recognition/
        ├── train_efficientnet.py
        └── build_shape_model.py
```

## Deployment Target

- **Host**: OnyxSoma (10.0.0.44)
- **Run Mode**: service (systemd)
- **Containers**: 2 (Ray head, FastAPI wrapper)
- **Networks**: host (direct access to workers)
- **Ports**: 9469 (API), 6379 (Ray), 8265 (Dashboard), 8000 (Serve)
