# Future Architecture

Planned architecture improvements for ChatOps v2.0 and beyond.

## Overview

The future architecture introduces:
- **Kafka** for event streaming
- **Redis** for distributed caching and state
- **Microservices** for better scalability
- **TimescaleDB** for optimized time-series storage

## Key Improvements

### 1. Kafka Integration

**Purpose**: Decouple services, enable event streaming, handle high throughput

**Topics**:
- `metrics-topic`: All metrics from agents (partitioned by server_id)
- `alerts-topic`: Alert creation/resolution events
- `commands-topic`: Command execution requests/responses
- `events-topic`: Connection events, audit logs, system events
- `logs-topic`: Application and system logs

**Benefits**:
- **Buffering**: Metrics buffered if API is down
- **Scalability**: Multiple consumers can process metrics
- **Replay**: Replay events for debugging/recovery
- **Event Sourcing**: Complete event history

### 2. Redis Integration

**Purpose**: Distributed caching, state management, pub/sub

**Use Cases**:
- **Agent Connection Registry**: `agent:connections:{server_id}` → connection metadata
- **Metrics Cache**: `metrics:latest:{server_id}` → latest metrics (TTL: 60s)
- **Session Store**: `session:{user_id}` → JWT refresh tokens
- **Rate Limiting**: `ratelimit:{user_id}:{endpoint}` → request counters
- **WebSocket Subscriptions**: `ws:subscribers:{server_id}` → Set of client IDs
- **Distributed Locks**: `lock:command:{server_id}` → prevent concurrent commands
- **Pub/Sub**: Real-time broadcasting to frontend clients

### 3. Microservices Architecture

**Service Breakdown**:

1. **Auth Service**: JWT, API keys, user authentication
2. **Server Service**: Server CRUD operations
3. **Metrics Service**: Metrics storage and retrieval
4. **Alert Service**: Threshold evaluation and alert management
5. **Command Service**: Command execution and routing
6. **WebSocket Service**: WebSocket connection management
7. **Notification Service**: Alert notifications (Email, Slack, etc.)
8. **Analytics Service**: Real-time aggregations and ML

### 4. TimescaleDB

**Purpose**: Optimized time-series storage

**Features**:
- Automatic partitioning by time
- Compression for old data
- Retention policies
- Continuous aggregates
- Better query performance

## Migration Path

### Phase 1: Add Redis (v1.5)
- Move agent connections to Redis
- Cache metrics in Redis
- Implement Redis pub/sub for real-time updates

### Phase 2: Add Kafka (v1.8)
- Introduce Kafka for metrics ingestion
- Keep WebSocket for commands (temporary)
- Dual-write: WebSocket + Kafka
- Gradually migrate consumers

### Phase 3: Microservices (v2.0)
- Split monolith into services
- Service-to-service via Kafka
- API Gateway for routing
- Service mesh for communication

### Phase 4: TimescaleDB (v2.1)
- Migrate metrics to TimescaleDB
- Implement compression/retention
- Optimize queries with continuous aggregates

## Technology Stack

**Infrastructure**:
- **Container Orchestration**: Kubernetes
- **Service Mesh**: Istio or Linkerd
- **API Gateway**: Kong, Traefik, or AWS API Gateway
- **Load Balancer**: NGINX, HAProxy, or cloud LB
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or Loki
- **Tracing**: Jaeger or Zipkin

**Message Queue**:
- **Kafka**: Event streaming, metrics ingestion
- **Redis Streams**: Lightweight alternative for some use cases

**Caching**:
- **Redis Cluster**: Distributed caching, pub/sub
- **Redis Sentinel**: High availability

**Database**:
- **PostgreSQL**: Primary database (users, servers, configs)
- **TimescaleDB**: Time-series metrics storage
- **Read Replicas**: For read-heavy operations

## Scalability Benefits

1. **Horizontal Scaling**: Each service can scale independently
2. **Fault Tolerance**: Service failures don't cascade
3. **High Throughput**: Kafka handles millions of metrics/second
4. **Low Latency**: Redis caching reduces database load
5. **Event Replay**: Debugging and recovery via Kafka
6. **Multi-Region**: Redis/Kafka support geo-distribution
7. **Cost Optimization**: Scale services based on load

## Security Enhancements

1. **API Gateway**: Centralized authentication/authorization
2. **Service Mesh**: mTLS between services
3. **Secrets Management**: Vault or AWS Secrets Manager
4. **Rate Limiting**: Redis-based distributed rate limiting
5. **Audit Logging**: All events to Kafka → Elasticsearch

## Comparison: Current vs Future

| Aspect | Current (v1.0) | Future (v2.0) |
|--------|----------------|---------------|
| **Scalability** | Single instance | Horizontal scaling |
| **State Management** | In-memory | Redis distributed |
| **Message Queue** | Direct WebSocket | Kafka event streaming |
| **Metrics Storage** | PostgreSQL | TimescaleDB |
| **Caching** | None | Redis cluster |
| **Service Architecture** | Monolith | Microservices |
| **Fault Tolerance** | Single point of failure | Service isolation |
| **Throughput** | Limited by single instance | Millions of events/sec |
| **Real-time Updates** | Direct WebSocket | Redis pub/sub + WebSocket |
| **Event History** | Database only | Kafka + Database |

## Next Steps

- [System Architecture](system-architecture.md)
- [Data Flow](data-flow.md)

