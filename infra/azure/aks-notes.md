# Azure Kubernetes Service Notes

AeroOps NoSQL Control Tower is designed to be deployable to Azure Kubernetes Service.

## Local Kubernetes Validation

The project was successfully deployed to local Kubernetes using Docker Desktop.

Validated resources:

- Namespace
- ConfigMap
- Secret
- Deployment
- Service
- Horizontal Pod Autoscaler
- Liveness probe
- Readiness probe
- CPU and memory requests/limits
- 2 API replicas

## Local Kubernetes Result

```text
deployment.apps/aeroops-api   2/2
pod/aeroops-api-xxxxx         1/1 Running
pod/aeroops-api-yyyyy         1/1 Running
```

## Azure Target

The same Kubernetes architecture can be adapted for AKS.

Target services:

- Azure Container Registry for the API image
- Azure Kubernetes Service for API deployment
- Azure Cosmos DB for MongoDB as the operational NoSQL database

## Required AKS Adjustments

For AKS, the deployment image should change from the local image:

```text
aeroops-nosql-control-tower-api:latest
```

to the ACR image:

```text
<acr-login-server>/aeroops-api:latest
```

The local setting:

```text
imagePullPolicy: Never
```

should be changed to:

```text
imagePullPolicy: IfNotPresent
```

or omitted.

## Secret Update

The Kubernetes Secret should use the Azure Cosmos DB for MongoDB connection string:

```yaml
stringData:
  MONGODB_URI: "<cosmos-db-mongodb-connection-string>"
```

## Deployment Validation

After applying manifests to AKS, validate:

```text
kubectl get pods -n aeroops
kubectl get svc -n aeroops
kubectl port-forward svc/aeroops-api-service 8000:80 -n aeroops
```

Then test:

```text
http://localhost:8000/health
http://localhost:8000/ready
http://localhost:8000/docs
```

## MVP Status

AKS real deployment was considered optional for the 12-hour MVP.

The project already validates Kubernetes readiness through Docker Desktop Kubernetes. Azure Container Registry was validated successfully by pushing the FastAPI image to ACR.
