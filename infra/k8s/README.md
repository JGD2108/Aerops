# Kubernetes Local Deployment

This folder contains Kubernetes manifests for running the AeroOps NoSQL Control Tower API on a local Kubernetes cluster using Docker Desktop.

## Resources

- `namespace.yaml`: creates the `aeroops` namespace.
- `configmap.yaml`: stores non-sensitive application configuration.
- `secret.example.yaml`: stores the MongoDB connection string for local development.
- `deployment.yaml`: deploys the FastAPI API with 2 replicas, resource requests/limits, liveness probe, and readiness probe.
- `service.yaml`: exposes the API internally as a ClusterIP service.
- `hpa.yaml`: defines a Horizontal Pod Autoscaler from 2 to 4 replicas based on CPU utilization.

## Local prerequisites

Docker Desktop Kubernetes must be enabled:

Docker Desktop → Settings → Kubernetes → Enable Kubernetes → Apply & Restart.

## Build the local image

```powershell
docker compose build api