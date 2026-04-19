# Informe Ejecutivo - SCADA Alarm Gateway and Migrator

## Resumen Ejecutivo

Este proyecto implementa una solucion completa para el caso **SCADA Alarm Gateway and Migrator**. La necesidad del cliente industrial es migrar historicos de alarmas SCADA desde archivos legacy CSV/JSON hacia una base relacional consultable, con control sobre datos sucios e inconsistentes.

La solucion entrega:

| Capacidad | Resultado |
| --- | --- |
| Dataset sintetico | Archivos CSV/JSON representativos con errores intencionales. |
| ETL robusto | Lectura, limpieza, normalizacion, validacion, deduplicacion y carga bulk. |
| Persistencia relacional | PostgreSQL con tablas para alarmas, batches y rechazos. |
| API | FastAPI con filtros, paginacion, metricas y errores estructurados. |
| Frontend | Dashboard SvelteKit con filtros, listado y metricas agregadas. |
| Operacion reproducible | Docker Compose para levantar base, API y frontend. |
| Calidad | Pruebas backend/frontend y validaciones manuales HTTP. |

## Por Que Esta Solucion Sirve

La solucion no solo carga datos: conserva trazabilidad del proceso y evita perdida silenciosa de informacion. En un contexto industrial, esto importa porque los historicos de alarmas suelen contener errores, pero esos errores tambien son informacion operativa. Por eso las filas invalidas se registran en `alarm_rejections` con payload original y motivo.

La API habilita que otros sistemas de planta consulten alarmas filtradas por tiempo, criticidad y tag, y tambien consuman metricas como top tags y resumen de distribuciones. El dashboard demuestra visualmente el consumo de la API sin cargar todo el dataset en memoria del navegador.

## Arquitectura de Componentes

![Arquitectura de componentes](diagrams/architecture-components.svg)

Fuente editable: [`diagrams/architecture-components.mmd`](diagrams/architecture-components.mmd)

## Flujo de Ingesta ETL

![Flujo ETL](diagrams/etl-flow.svg)

Fuente editable: [`diagrams/etl-flow.mmd`](diagrams/etl-flow.mmd)

## Operacion de la Demo

![Operacion Docker Compose](diagrams/operation-sequence.svg)

Fuente editable: [`diagrams/operation-sequence.mmd`](diagrams/operation-sequence.mmd)

## Flujo de Consulta

![Flujo de consulta API](diagrams/api-request-flow.svg)

Fuente editable: [`diagrams/api-request-flow.mmd`](diagrams/api-request-flow.mmd)

## Modelo de Datos

![Modelo de datos](diagrams/data-model.svg)

Fuente editable: [`diagrams/data-model.mmd`](diagrams/data-model.mmd)

## Cumplimiento del PDF

Fuente revisada: PDF provisto por el usuario, **SCADA Alarm Gateway and Migrator**, revision 1.0, fecha 2025-04-15.

| Requisito del caso | Estado | Evidencia |
| --- | --- | --- |
| Generar dataset representativo CSV/JSON con problemas de calidad | Cumple | `api/scripts/generate_dataset.py`, `api/data/raw/alarms_dataset.csv`, `api/data/raw/alarms_dataset.json`. |
| Ingesta, limpieza y normalizacion | Cumple | `api/app/ingestion/readers.py`, `parsers.py`, `transformers.py`, `loaders.py`. |
| Base de datos relacional | Cumple | PostgreSQL con SQLAlchemy y Alembic. |
| API en Python | Cumple | FastAPI en `api/app/main.py`. |
| Consultar alarmas por tiempo, criticidad y tag | Cumple | `GET /api/v1/alarms`. |
| Endpoint de agregacion | Cumple | `GET /api/v1/metrics/top-tags` y `GET /api/v1/metrics/summary`. |
| Validar entradas y manejar errores | Cumple | Pydantic, handlers globales y respuestas JSON estructuradas. |
| README con instrucciones y decisiones | Cumple | `README.md`. |
| Docker reproducible | Cumple | `docker-compose.yml`, `api/Dockerfile`, `web/Dockerfile`. |
| Pruebas | Cumple | `api/tests`, `web/src/lib/*.test.ts`, `Dashboard.test.ts`. |
| Escalabilidad basica | Cumple | Indices, paginacion, carga bulk por chunks. |
| Seguridad basica | Cumple parcialmente | CORS configurable, validacion, no stack traces al cliente; autenticacion fuera de alcance. |
| Frontend opcional | Cumple | Dashboard SvelteKit. |
| Postman | Cumple parcialmente | Se validaron endpoints por HTTP/curl; no se entrega coleccion Postman formal. |

## Decisiones Tecnicas y Justificacion

| Decision | Justificacion |
| --- | --- |
| FastAPI | Permite OpenAPI automatico, validacion declarativa y endpoints claros. |
| SQLAlchemy + Alembic | Facilita modelo relacional versionado y migraciones reproducibles. |
| PostgreSQL | Equivalente robusto a SQL Server para demo relacional, indices y constraints. |
| Tabla de rechazos | Permite auditar datos invalidos sin descartarlos silenciosamente. |
| Batches de ingesta | Da trazabilidad por archivo y resumen operativo de cada carga. |
| Carga bulk | Evita inserciones fila a fila y escala mejor para volumenes altos. |
| Paginacion | Protege API/frontend ante datasets grandes. |
| SvelteKit | Permite demostrar consumo real de API con dashboard simple y mantenible. |
| Docker Compose | Reduce friccion para evaluacion y sustentacion. |
| `psycopg` v3 | Evita problemas de compatibilidad local con Python 3.14 y reemplaza `psycopg2`. |

## Supuestos del Dataset

| Supuesto | Detalle |
| --- | --- |
| Volumen base | 2000 registros validos con seed 42. |
| Errores agregados | Aproximadamente 10% de registros con problemas y 30 duplicados. |
| Sistemas fuente | Siemens SCADA, ABB SCADA, Honeywell DCS y Rockwell PLC. |
| Criticidad valida | `HIGH`, `MEDIUM`, `LOW`. |
| Estados esperados | `ACTIVE`, `ACKNOWLEDGED`, `CLEARED`, `SHELVED`. |
| Fechas | ISO y formatos alternativos para probar normalizacion. |
| Duplicado de negocio | `external_alarm_id`, `event_time`, `tag`. |

## Evidencia de Validacion

Comandos usados para validar:

```powershell
cd D:\Proyectos\Soap\Test\api
.\.venv\Scripts\python.exe -m pytest
```

```powershell
cd D:\Proyectos\Soap\Test\web
npm run check
npm test
npm run build
```

```powershell
cd D:\Proyectos\Soap\Test
docker compose up --build -d api web
curl.exe -s http://localhost:8000/api/v1/health
curl.exe -s http://localhost:8000/api/v1/metrics/summary
curl.exe -s -o NUL -w "%{http_code}" http://localhost:3000
```

Resultados esperados:

| Validacion | Resultado esperado |
| --- | --- |
| Backend tests | 68 pruebas pasando. |
| Frontend check | 0 errores, 0 warnings. |
| Frontend tests | 7 pruebas pasando. |
| Build web | Build exitoso. |
| Health API | `{"status":"ok","db":"connected"}`. |
| Dashboard | HTTP 200 en `localhost:3000`. |

Resumen de la corrida backend reportada:

| Dato | Resultado |
| --- | --- |
| Plataforma | Windows, Python 3.14.0. |
| Pytest | 9.0.3. |
| Tests recolectados | 68. |
| Resultado | 68 passed. |
| Warnings | 86 conocidos. |
| Duracion | 3.13s. |

Cobertura backend destacada en la corrida:

| Area | Evidencia |
| --- | --- |
| Metricas de charts | `test_charts_metrics`. |
| Filtros y bucket por hora | `test_charts_metrics_supports_filters_and_hour_bucket`. |
| Validacion de bucket invalido | `test_charts_invalid_bucket_returns_422`. |

## Limitaciones Honestas

| Limitacion | Impacto | Mejora recomendada |
| --- | --- | --- |
| Sin autenticacion | No debe exponerse como API publica real. | Agregar JWT/OIDC o API keys. |
| Sin coleccion Postman formal | El PDF lo recomienda, aunque se probaron endpoints por `curl`. | Crear coleccion Postman o Bruno. |
| Warnings por `datetime.utcnow()` | No rompe la demo, pero es deuda tecnica. | Migrar a `datetime.now(datetime.UTC)`. |
| Tests usan SQLite | Rapidos, pero no cubren todas las diferencias PostgreSQL. | Agregar pruebas con PostgreSQL/Testcontainers. |
| Volumen Docker acumulable | Los conteos crecen si no se resetea el volumen. | Usar `docker compose down -v` antes de demo limpia. |
| Observabilidad basica | Logs suficientes para demo, no para produccion. | Agregar logs estructurados, metricas y tracing. |

## Guion Breve de Sustentacion

1. Presentar el problema: historicos SCADA en CSV/JSON con errores reales de calidad.
2. Mostrar la arquitectura: dataset, ETL, PostgreSQL, API y dashboard.
3. Explicar el ETL: parseo, normalizacion, validacion, rechazos y carga bulk.
4. Mostrar el modelo: `alarms`, `ingestion_batches`, `alarm_rejections`.
5. Demostrar API: `/health`, `/alarms`, `/metrics/top-tags`, `/metrics/summary`.
6. Abrir el dashboard y aplicar filtros.
7. Explicar decisiones: trazabilidad, paginacion, indices, Docker y pruebas.
8. Cerrar con limitaciones: autenticacion fuera de alcance, Postman pendiente formal, mejoras futuras.

## Comandos de Demo

```powershell
cd D:\Proyectos\Soap\Test
docker compose down -v
docker compose up --build
```

En otra terminal:

```powershell
curl.exe http://localhost:8000/api/v1/health
curl.exe "http://localhost:8000/api/v1/alarms?page=1&page_size=5"
curl.exe http://localhost:8000/api/v1/metrics/top-tags
curl.exe http://localhost:8000/api/v1/metrics/summary
```

Abrir:

```text
http://localhost:8000/docs
http://localhost:3000
```
