# Changelog

All notable changes to this project are documented in this file.

## [0.2.0] - 2026-04-10

### Milestone 1 - Core Architecture
- Bootstrapped full-stack repository with `backend-java`, `ai-service`, and `frontend`.
- Implemented RAG + ReAct core flow and SSE chat experience.
- Added local model/vector integration foundations (Ollama + Chroma adapters).

### Milestone 2 - Security
- Added Spring Security filter chain and JWT token validation.
- Introduced login API and authentication DTO contracts.
- Added global exception handling and standardized error payloads.

### Milestone 3 - Observability & Ops
- Added OpenTelemetry tracing pipeline via OTel Collector.
- Added Prometheus metrics export and Grafana/Jaeger visualization stack.
- Added Docker Compose orchestration and bootstrap scripts for local runtime.

### Milestone 4 - Testing
- Added Python unit/integration tests for ingestion, tools, and stream API.
- Added SpringBootTest integration for auth and backend endpoints.
- Added Playwright E2E flow and k6 load test scripts.

### Milestone 5 - CI & Documentation
- Added GitHub Actions workflow for `lint -> test -> build -> docker-push`.
- Updated README with architecture, testing matrix, and milestone timeline.
- Added contribution-oriented project packaging for job/interview showcase.

