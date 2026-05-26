# Explicacion del Proyecto AeroOps NoSQL Control Tower

## 1) Que es este proyecto

AeroOps NoSQL Control Tower es una plataforma operacional para datos de aviacion/travel construida para demostrar capacidades de Data Engineering orientadas a NoSQL.

Objetivo principal:

- Modelar datos operacionales de vuelos en MongoDB.
- Exponer patrones de acceso de negocio por API (FastAPI).
- Agregar una capa de analitica operacional (endpoints + dashboard).
- Dejar una ruta cloud-native hacia Azure.

---

## 2) Problema que resuelve

Este proyecto busca responder preguntas operativas como:

- Que vuelos estan retrasados hoy.
- Que rutas muestran peor desempeno.
- Que aeropuertos concentran cancelaciones.
- Que pasajeros/itinerarios quedan impactados.
- Que corridas del pipeline se ejecutaron y con que resultado.

---

## 3) Arquitectura funcional

```text
CSV BTS + OurAirports
        ->
Procesamiento Python
        ->
Colecciones MongoDB operacionales
        ->
FastAPI (consultas operacionales + agregaciones)
        ->
Streamlit Dashboard (Live/Snapshot)
```

Version cloud agregada:

```text
Azure Blob Storage (raw/processed)
        ->
Pipeline batch (run_pipeline)
        ->
Cosmos DB for MongoDB
        ->
Container Apps Jobs (manual/schedule)
```

---

## 4) Componentes y por que existen

### API (`app/`)
- FastAPI sirve como capa de acceso operacional.
- Evita que dashboard o clientes toquen MongoDB directo.
- Permite estandarizar contratos de consulta.

### Scripts (`scripts/`)
- Separan ingestion, transformacion, carga, enrichment e indices.
- `run_pipeline.py` orquesta todo en un solo comando auditable.
- `audit_runs` registra trazabilidad de procesos.

### Dashboard (`dashboard/`)
- Streamlit para mostrar analitica operacional rapido.
- Consume API, no base de datos directa.
- Vistas orientadas a operacion: resumen, rutas, aeropuertos, impacto.

### Infra (`infra/`)
- Dockerfile API.
- Docker Compose para entorno local completo.
- Manifiestos Kubernetes para ruta de despliegue.

---

## 5) Modelo de datos NoSQL

Colecciones principales:

- `flights`: hechos operacionales de vuelo.
- `airports`: catalogo de aeropuertos.
- `flight_events`: timeline derivado por vuelo.
- `passenger_itineraries`: impacto de pasajeros (sintetico).
- `audit_runs`: control de procesos.
- `ops_metrics_snapshots`: snapshots analiticos.

Razon de diseno:

- Documentos orientados a consultas de negocio.
- Indices definidos por patron de acceso, no por campo arbitrario.

---

## 6) Endpoints clave (como usarlo)

Operacional:

- `GET /flights/{flight_id}`
- `GET /flights/status/{status}`
- `GET /flights/origin/{origin}`
- `GET /flights/{flight_id}/events`
- `GET /flights/{flight_id}/impacted-passengers`

Analitica:

- `GET /ops/delay-summary`
- `GET /ops/top-delayed-routes`
- `GET /ops/cancellations-by-airport`
- `GET /ops/passenger-impact-summary`
- `GET /ops/metrics-snapshots/latest`

Auditoria:

- `GET /audit/runs`

Health:

- `GET /health`
- `GET /ready`

---

## 7) Paso a paso para correrlo (recomendado)

## Opcion A: Docker Compose (ruta principal)

1. Abrir terminal en raiz del repo.  
2. Ejecutar:

```powershell
docker compose up --build
```

3. Abrir API docs:

```text
http://localhost:8000/docs
```

4. Abrir dashboard:

```text
http://localhost:8501
```

5. Validar health:

```text
http://localhost:8000/health
http://localhost:8000/ready
```

## Opcion B: Pipeline por scripts (sin compose)

1. Procesar raw:

```powershell
python scripts/process_raw_data.py
```

2. Cargar datos e indices:

```powershell
python -m scripts.load_airports
python -m scripts.load_flights
python -m scripts.create_indexes
```

3. Generar enriquecimientos:

```powershell
python -m scripts.generate_events
python -m scripts.generate_passengers
python -m scripts.build_analytics_snapshots
```

4. O correr todo junto:

```powershell
python -m scripts.run_pipeline
```

---

## 8) Paso a paso para usarlo (demo funcional)

1. Ir a Swagger (`/docs`).  
2. Ejecutar `GET /ops/delay-summary`.  
3. Ejecutar `GET /ops/top-delayed-routes?limit=5&min_flights=10`.  
4. Ejecutar `GET /ops/passenger-impact-summary`.  
5. Ejecutar `GET /audit/runs?limit=10`.  
6. Ir a dashboard y revisar tabs: Overview, Routes, Airport, Passenger, Audit.

---

## 9) Que se implemento y por que (resumen tecnico)

- Capa operacional NoSQL: para consultas de alta frecuencia por entidad/estado.
- Capa analitica por agregaciones: para KPIs operativos sin crear BI separado.
- Snapshots analiticos: para materializar metricas y habilitar historico.
- Orquestador `run_pipeline`: para ejecucion batch repetible.
- Storage abstraction (`local` / `azure_blob`): para mover pipeline local->cloud.
- Azure Container Apps Jobs: para scheduler/manual runs de pipeline.
- Log Analytics: para diagnosticar ejecuciones batch.
- Endurecimiento Cosmos:
  - retry para errores 429 (`code 16500`),
  - deduplicacion en carga de vuelos,
  - creacion de indices idempotente.

---

## 10) Estado actual Azure (honesto)

Provisionado:

- ACR: `aeroopsacr1974`
- Container Apps Env: `aeroops-ca-env`
- Jobs: manual + scheduled
- Log Analytics: `aeroops-law`
- Cosmos MongoDB: `aeroops-cosmos-mongo`

Limitacion actual:

- El pipeline cloud puede seguir recibiendo throttling 429 en fases de carga pesada.
- Para cerrar 100% green se requiere ajustar throughput/estrategia incremental de carga en Cosmos.

---

## 11) Como mejorar para produccion

- Evitar full reload diario; migrar a upserts incrementales por particion temporal.
- Subir/autoescalar RU en ventanas de carga.
- Ajustar tamano de lotes segun RU real y `RetryAfterMs`.
- Separar ingestion y analytics en jobs distintos.
- Agregar alertas de fallos y metricas de duracion por step.

---

## 12) En una frase para entrevista

Proyecto de plataforma operacional NoSQL para aviacion con API FastAPI, Mongo/Cosmos, pipeline batch auditable, analitica operacional y dashboard, desplegable en contenedores y preparado para automatizacion cloud.
