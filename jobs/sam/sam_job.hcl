job "sam-inference" {
  datacenters = ["onyx-dc"]
  type        = "service"
  priority    = 75

  group "sam" {
    count = 1

    constraint {
      attribute = "${node.hostname}"
      value     = "onyxcortex"
    }

    task "sam-inference" {
      driver = "docker"

      config {
        image   = "sam-inference:v1"
        command = "python3"
        args    = ["/app/sam_server.py"]

        mount {
          type   = "bind"
          target = "/app"
          source = "/opt/onyx/skills/ml-compute/jobs/sam"
        }

        mount {
          type   = "bind"
          target = "/models"
          source = "/mnt/ml-store/sam-models"
        }
      }

      resources {
        cpu    = 4000
        memory = 12288

        device "nvidia/gpu" {
          count = 1
        }
      }

      env {
        CUDA_VISIBLE_DEVICES = "0"
      }
    }
  }
}
