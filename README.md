# worker-push-api-python
An example of reliable Push API microservice written in Python. This implementation can be used as a starting point to develop a production ready worker for the Ingestion layer of a Dataplatform.
The componet implementa a bucket approach to collect the payload received via a PUT Rest Api. The bucket will be flushed on overflow and/or overtime reached.
The model is equipped with several fields for data lineage and data-plumbing and the write (on the Datalake) is schemaless (schema on write).
The component is also dockerized, the Dockerfile is available, and there are all the step required for the provisioning on Kubernetes and the monitoring with Prometheus and Grafana.
