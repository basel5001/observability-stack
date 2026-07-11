# Observability Stack

![CI](https://github.com/basel5001/observability-stack/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white)
![Loki](https://img.shields.io/badge/Loki-2C3239?style=flat-square&logo=grafana&logoColor=white)
![Tempo](https://img.shields.io/badge/Tempo-F46800?style=flat-square&logo=grafana&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

Self-hosted observability platform -- a Datadog alternative built on open-source components. One command to deploy a full metrics, logging, tracing, and alerting stack with AI-powered anomaly analysis.

## Architecture

```
                    +------------------+
                    |     Grafana      |  :3000 (Dashboards)
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v-----+  +-----v------+
     | Prometheus  |  |    Loki    |  |   Tempo    |
     |  (Metrics)  |  |   (Logs)   |  |  (Traces)  |
     +------+------+  +------------+  +-----+------+
            |              :3100        :3200 | :4317
    +-------+-------+                        |
    |               |                  OTLP gRPC
+---v---+     +-----v-----+
| Node  |     |  cAdvisor  |
|Exporter|    | (Containers)|
+--------+    +------------+
  :9100          :8080

     +-----------------+       +------------------+
     |  Alertmanager   | ----> |   AI Analyzer    |
     |   (Routing)     |       | (Bedrock / LLM)  |
     +-----------------+       +------------------+
        :9093                       :8000
```

## Quick Start

```bash
# Clone and configure
cp .env.example .env
# Edit .env with your credentials

# Start everything
docker compose up -d

# Or use Make
make up
```

## Accessing Services

| Service        | URL                    | Description              |
| -------------- | ---------------------- | ------------------------ |
| Grafana        | http://localhost:3000   | Dashboards & exploration |
| Prometheus     | http://localhost:9090   | Metrics & query          |
| Alertmanager   | http://localhost:9093   | Alert management         |
| Loki           | http://localhost:3100   | Log aggregation          |
| Tempo          | http://localhost:3200   | Distributed tracing      |
| AI Analyzer    | http://localhost:8000   | AI anomaly analysis      |
| Node Exporter  | http://localhost:9100   | Host metrics             |
| cAdvisor       | http://localhost:8080   | Container metrics        |

Default Grafana login: `admin` / value of `GF_SECURITY_ADMIN_PASSWORD` (default: `admin`). Anonymous read access is enabled.

## Pre-built Dashboards

- **Node Overview** -- CPU, memory, disk I/O, and network traffic
- **Container Overview** -- Per-container CPU, memory, and network from cAdvisor

## Adding Custom Scrape Targets

Edit `configs/prometheus/prometheus.yml` and add a new job:

```yaml
scrape_configs:
  - job_name: "my-service"
    static_configs:
      - targets: ["my-service:8080"]
    metrics_path: /metrics
```

Then reload Prometheus:

```bash
curl -X POST http://localhost:9090/-/reload
```

## AI Features

The AI Analyzer uses AWS Bedrock to provide intelligent observability:

### Analyze Metrics

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "cpu_usage",
    "values": [45, 47, 82, 95, 98, 97, 99],
    "threshold": 80
  }'
```

### Automatic Alert Explanation

Alertmanager is configured to forward alerts to the AI Analyzer, which returns root cause analysis and suggested remediation.

**Requirements:** Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` in `.env`.

## Alert Configuration

Alerts are defined in `configs/prometheus/alert_rules.yml`:

| Alert              | Condition                   | Duration |
| ------------------ | --------------------------- | -------- |
| HighCPU            | CPU > 80%                   | 5m       |
| HighMemory         | Memory > 85%                | 5m       |
| InstanceDown       | Target unreachable           | 1m       |
| DiskSpaceLow       | Disk < 10% free             | 5m       |
| HighErrorRate      | 5xx rate > 5%               | 5m       |
| ContainerRestarting| > 3 restarts in 15m         | 5m       |

Configure notification channels in `configs/alertmanager/alertmanager.yml`.

## Make Targets

```
make up        Start the stack
make down      Stop the stack
make restart   Restart the stack
make logs      Tail logs
make status    Show service status
make clean     Stop and remove volumes
make build     Rebuild ai-analyzer image
```

## License

MIT
