job "sam-inference" {
  datacenters = ["onyx-dc"]
  type        = "service"
  priority    = 75

  group "sam" {
    count = 1

    # Affinity (préférence soft) au lieu de constraint stricte
    # Permet au job de s'exécuter ailleurs si nécessaire
    affinity {
      attribute = "${node.Name}"
      value     = "onyxcortex"
      weight    = 100  # Préfère OnyxCortex
    }

    task "sam-inference" {
      driver = "docker"

      config {
        image   = "sam-inference:v1"
        command = "python3"
        args    = ["/app/sam_server.py"]

        # sam_server.py est déjà COPY dans l'image
        # Les volumes bind mounts ne sont pas supportés par ce driver Nomad
        # Donc on utilise juste les chemins standard dans l'image
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
