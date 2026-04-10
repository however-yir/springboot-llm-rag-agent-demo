# Deployment (One-Command)

## 1) Prepare model runtime

```bash
./scripts/bootstrap_models.sh
```

## 2) Start full stack

```bash
docker compose up -d
```

## 3) Access entry points

- Web UI: `http://localhost`
- Backend Health: `http://localhost/api/java/actuator/health`
- AI Health: `http://localhost/api/ai/health`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (`admin / admin123456`)
- Jaeger: `http://localhost:16686`

## 4) API smoke test

```bash
curl -X POST http://localhost/api/java/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456"}'
```

## 5) Run quality gates

```bash
make lint
make test
```
