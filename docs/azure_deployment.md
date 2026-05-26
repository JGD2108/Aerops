# Azure Deployment Path

AeroOps NoSQL Control Tower is designed to be Azure-ready.

The target Azure architecture uses:

- Azure Cosmos DB for MongoDB as the operational NoSQL database.
- Azure Container Registry to store the FastAPI Docker image.
- Azure Kubernetes Service to run the API using Kubernetes manifests.

## Target Architecture

BTS / OurAirports data
→ Python ingestion scripts
→ Azure Cosmos DB for MongoDB
→ FastAPI operational API
→ Docker image
→ Azure Container Registry
→ Azure Kubernetes Service

## Local-to-Azure Mapping

| Local Component | Azure Target |
|---|---|
| Local MongoDB container | Azure Cosmos DB for MongoDB |
| Local Docker image | Azure Container Registry |
| Docker Desktop Kubernetes | Azure Kubernetes Service |
| Local `.env` / Kubernetes Secret | Azure Key Vault or Kubernetes Secret |
| Local processed CSV files | Azure Blob Storage or scheduled ingestion job |

## Deployment Strategy

1. Create a resource group.
2. Create Azure Container Registry.
3. Build and push the FastAPI Docker image.
4. Create Azure Cosmos DB for MongoDB.
5. Update Kubernetes Secret with the Cosmos DB MongoDB connection string.
6. Create or connect to AKS.
7. Apply Kubernetes manifests.
8. Validate `/health`, `/ready`, and `/docs`.

## Important Note

The local MVP does not depend on Azure. If Azure deployment is blocked by quota, billing, permissions, or time constraints, the project remains valid because the local Docker and Kubernetes deployment paths are already working.

## Azure Subscription Validation

The Azure CLI was authenticated successfully using the `Azure for Students` subscription.

The following Azure resource providers are required for the target deployment path:

| Azure Service | Provider Namespace |
|---|---|
| Azure Container Registry | Microsoft.ContainerRegistry |
| Azure Kubernetes Service | Microsoft.ContainerService |
| Azure Cosmos DB for MongoDB | Microsoft.DocumentDB |

At validation time, the providers were not registered yet, so the next step is to register them using:

```powershell
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.DocumentDB
```

## Azure Container Registry Validation

Azure Container Registry was successfully validated for the project.

The local FastAPI Docker image was tagged and pushed to ACR.

Local image:

```text
aeroops-nosql-control-tower-api:latest
```

ACR repository:

```text
aeroops-api
```

ACR tag:

```text
latest
```

Validation commands:

```powershell
az acr repository list --name <acr-name> --output table
az acr repository show-tags --name <acr-name> --repository aeroops-api --output table
```

Validation result:

```text
Repository: aeroops-api
Tag: latest
```

This confirms that the project has a working container image promotion path from local Docker to Azure Container Registry. This is the required step before deploying the API image to Azure Kubernetes Service.

## Qué haremos después

Si los providers quedan `Registered`, recomiendo intentar primero ACR, no AKS.

Orden más seguro:

```text
1. ACR -> subir imagen Docker
2. Cosmos DB notes -> documentar conexión MongoDB-compatible
3. AKS -> solo si hay tiempo y cuota
```


## AKS Deployment Path

The local Kubernetes deployment provides the baseline for an AKS deployment.

To deploy to AKS, the following changes would be required:

1. Use the ACR image instead of the local Docker image.
2. Replace `imagePullPolicy: Never` with `IfNotPresent` or remove it.
3. Configure AKS permissions to pull from ACR.
4. Replace the local MongoDB connection string with the Azure Cosmos DB for MongoDB connection string.
5. Apply the Kubernetes manifests to the AKS cluster.
6. Validate `/health`, `/ready`, and `/docs`.

## Azure Validation Summary

The Azure CLI was authenticated successfully using the Azure for Students subscription.

The required providers were registered:

- `Microsoft.ContainerRegistry`
- `Microsoft.ContainerService`
- `Microsoft.DocumentDB`

Azure Container Registry was validated successfully:

- Repository: `aeroops-api`
- Tag: `latest`

AKS and Cosmos DB were documented as the target deployment path, but they were not required to complete the MVP because the project already runs successfully with Docker Compose and local Kubernetes.