# Progress Log

## Week 1 - Complete
- AKS cluster deployed (Central India, 1 node)
- Keycloak 19 deployed with OIDC realm `iam-observability-lab`
- Client `protected-service-a` configured, token issuance verified
- Service A (FastAPI) validates JWT tokens end-to-end

## Week 2 - Complete
- OTel Collector deployed, receiving spans from Service A
- Custom span attributes: token.valid, validation_latency_ms, failure_reason
- Prometheus + Grafana stack deployed
- IAM Observability dashboard created via Grafana API

## Note
- Azure account was deleted after Week 2. Infra needs to be rebuilt
  on a new Azure subscription. All Helm values, Keycloak config,
  Service A code, and Grafana dashboard JSON are preserved in this repo.

## Next: Week 3
- Rebuild AKS cluster on new Azure account
- Service B with SAML
- ADRs
- README polish + GitHub Actions
