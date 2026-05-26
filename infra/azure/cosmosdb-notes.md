# Azure Cosmos DB for MongoDB Notes

AeroOps NoSQL Control Tower is designed to use Azure Cosmos DB for MongoDB as the cloud NoSQL operational database.

## Purpose

In the local MVP, MongoDB runs as a Docker container.

In the Azure target architecture, this local MongoDB instance can be replaced by Azure Cosmos DB for MongoDB.

## Local Component

```text
MongoDB container
mongodb://localhost:27017
```

## Azure Target

```text
Azure Cosmos DB for MongoDB
```

## Collections

The same MongoDB-style collections can be used:

- flights
- flight_events
- passenger_itineraries
- airports
- audit_runs

## Required Application Change

The FastAPI application already reads the MongoDB connection string from:

```text
MONGODB_URI
```

For Azure, the Kubernetes Secret would be updated with the Cosmos DB MongoDB connection string.

Example:

```yaml
stringData:
  MONGODB_URI: "<cosmos-db-mongodb-connection-string>"
```

## Indexing Considerations

The project currently creates indexes through:

```text
scripts/create_indexes.py
```

These indexes support operational access patterns such as:

- Flight lookup by flight_id
- Flights by origin and date
- Flights by status and date
- Flight event timelines
- Impacted passenger lookup
- Audit run review

## Sharding / Partitioning Consideration

For a larger Azure deployment, the suggested logical partitioning strategy is based on:

```text
{ flight_date: 1, origin: 1 }
```

This supports common aviation operational queries by date and airport.

Alternative shard/partition strategies:

```text
{ airline: 1, flight_date: 1 }
{ origin: 1, scheduled_departure: 1 }
```

## MVP Status

Cosmos DB was not required for the local MVP because the project already runs successfully with Dockerized MongoDB and local Kubernetes.

The application is Cosmos-ready because database connectivity is controlled through environment variables and Kubernetes Secrets.
