# Reliable Push-API Ingestion Microservice (Python)

A reference implementation of a reliable push-API ingestion worker in Python, designed as the starting point for a production-ready ingestion layer of a data platform.

Ingestion: payloads received through a REST PUT endpoint.
Buffering: a bucket-based micro-batching strategy, flushed on size threshold or time window, whichever comes first. This balances throughput against latency and reduces small-file writes on the data lake.
Data governance: each record carries lineage and data-plumbing metadata, so every event can be traced back to its origin.
Storage: schemaless writes to the data lake (schema-on-read), decoupling ingestion from downstream schema evolution.
Operations: Dockerfile included, step-by-step Kubernetes provisioning, and monitoring with Prometheus and Grafana.

Stack: Python, REST, Docker, Kubernetes, Prometheus, Grafana, data lake.
