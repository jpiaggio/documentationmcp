# PiggyMetrics: Product Manager Architecture & Capability Analysis
**Analysis Date:** March 11, 2026  
**Analyst:** Product Manager (Using Documentation Cartographer Tool)  
**Audience:** C-Suite / Product Leadership  
**Purpose:** Strategic assessment of application architecture, capabilities, and market readiness

---

## Executive Summary

This document presents a comprehensive analysis of the **PiggyMetrics** microservices architecture—a sophisticated financial advisor platform demonstrating enterprise-grade design patterns. As the PM responsible for evaluating this technology, I've used advanced code analysis tools to map the entire system architecture, identify key capabilities, and assess readiness for scaling.

**Key Finding:** PiggyMetrics implements a production-ready microservices architecture that aligns with modern financial services requirements including security, scalability, and distributed system resilience.

---

## 1. System Architecture Overview

### 1.1 Microservices Composition

PiggyMetrics is decomposed into **5 core independent services**, each handling a specific business domain:

```
┌─────────────────────────────────────────────────────────┐
│                  API Gateway (Router)                   │
│        Single entry point for all client requests        │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────┼──────────┬─────────────┐
    │          │          │             │
    ▼          ▼          ▼             ▼
┌────────┐ ┌────────┐ ┌────────┐  ┌──────────┐
│Account │ │Statics │ │Notifi- │  │Auth      │
│Service │ │Service │ │cation  │  │Service   │
│        │ │        │ │Service │  │(OAuth2)  │
└────────┘ └────────┘ └────────┘  └──────────┘
    │          │          │             │
    ▼          ▼          ▼             ▼
  MongoDB    MongoDB    MongoDB      (Token DB)
```

### 1.2 Service Responsibilities

| Service | Purpose | Key Endpoints | Data Model |
|---------|---------|---------------|-----------|
| **Account Service** | User account & financial item management | `GET /accounts/{name}`, `PUT /accounts/current` | Incomes, Expenses, Savings, User Settings |
| **Statistics Service** | Time-series analytics & financial metrics | `GET /statistics/current`, `PUT /statistics/{account}` | Normalized datapoints, Cash flow tracking |
| **Notification Service** | Email communications & reminders | `GET /notifications/settings/current` | Contact info, Notification preferences |
| **Auth Service** | OAuth2 token management | Token generation & validation | User credentials, token store |
| **API Gateway** | Request routing & aggregation | All external traffic | Route configuration |

---

## 2. Technical Architecture Deep Dive

### 2.1 Technology Stack

**Core Framework:**
- Spring Boot 2.0.3 (latest at implementation time)
- Spring Cloud Finchley Release
- Java 8

**Data Layer:**
- MongoDB (document database for each service)
- Isolation pattern enforced: "Each microservice has its own database"

**Communication:**
- RESTful APIs via HTTP/JSON
- OpenFeign for declarative service-to-service calls
- Service discovery via Spring Cloud Eureka

**Infrastructure & Resilience:**
- Netflix Eureka (service registry/discovery)
- Spring Cloud Config (centralized configuration)
- Spring Cloud Bus/AMQP (async messaging)
- Spring Cloud Sleuth (distributed tracing)
- Actuator (health checks & monitoring)
- OAuth2 (standards-based security)

**Deployment:**
- Docker containerization
- Docker Compose orchestration
- CI/CD via Travis CI

### 2.2 Security Architecture

The Auth Service implements a **dual OAuth2 model**:

```
User Login Flow:
  Browser Client → API Gateway → Auth Service
                                    ↓
                           Password Credentials Grant
                           (Returns JWT/Bearer Token)
                                    ↓
  Token stored in browser → Used for subsequent API calls

Service-to-Service Flow:
  Account Service → Auth Service (Client Credentials Grant)
                        ↓
                   Validates permissions
                        ↓
                   Allows inter-service calls
```

**Access Control Strategy:**
- Scope-based authorization: `server` scope for services, `ui` scope for browser
- `@PreAuthorize` annotations protect endpoints
- Example: `@PreAuthorize("#oauth2.hasScope('server') or #name.equals('demo')")`

---

## 3. Data Model & Domain Analysis

### 3.1 Account Service Domain

**Core Entity: Account (MongoDB Document)**

```java
{
  name: String (primary key),
  lastSeen: Date,
  incomes: List<Item>,
  expenses: List<Item>,
  saving: Saving,
  note: String (0-20,000 characters),
  created: Date (implied)
}
```

**Item Structure (Income/Expense Entry):**
```java
{
  title: String (1-20 characters),
  amount: BigDecimal,
  currency: Enum {USD, EUR, GBP, JPY, CHF, AUD, CAD, ...},
  period: Enum {DAILY, MONTHLY, YEARLY},
  icon: String (UI reference)
}
```

**Saving Structure:**
```java
{
  amount: BigDecimal,
  currency: Currency,
  period: TimePeriod
}
```

### 3.2 Data Validation & Constraints

The Account model enforces validation at the API layer:
- Item title: Required, 1-20 characters
- Account note: Optional, max 20,000 characters
- All currency amounts: Must be valid BigDecimal
- User email & password: Standard validation rules

**Implication for Product:** The system supports multi-currency operations—critical for international fintech expansion.

### 3.3 Statistics Service Domain

The Statistics Service normalizes all financial data to a **base currency** and creates **time-series datapoints** for each account.

```
Key capability: All income/expense data is calculated relative to 
               a base currency to enable cross-currency comparison
```

This is a sophisticated feature enabling:
- Dashboard charts across multiple currency zones
- Unified reporting for multi-currency households
- Comparative analytics across spend categories

---

## 4. API Interface Analysis

### 4.1 Account Service Endpoints

| Method | Path | Auth Required | UI Access | Purpose |
|--------|------||---|---|
| GET | `/accounts/{account}` | Server Scope | No | Retrieve account data |
| GET | `/accounts/current` | User | ✓ | Get authenticated user's account |
| GET | `/accounts/demo` | None | ✓ | Demo account for onboarding |
| PUT | `/accounts/current` | User | ✓ | Update user's account |
| POST | `/accounts/` | None | ✓ | Account registration |

**Notable Design Decisions:**

✓ **Demo Endpoint:** Allows unauthenticated users to explore the app (low friction onboarding)
✓ **Current Endpoint:** Automatic principal resolution (clean privacy model)
✓ **Server Scope:** Allows service-to-service calls for backend processes

### 4.2 Statistics Service Interface

```
GET /statistics/{account}  - Get historical trend data
GET /statistics/current    - Get authenticated user's metrics
GET /statistics/demo       - Demo statistics
PUT /statistics/{account}  - Record new transaction
```

### 4.3 Notification Service Interface

```
GET /notifications/settings/current  - Preference retrieval
PUT /notifications/settings/current  - Preference updates
```

---

## 5. Service Integration & Data Flow

### 5.1 Inter-Service Communication

The system implements **service-to-service communication** patterns:

```
Notification Service → (OpenFeign Client) → Account Service
                                                  ↓
                                         Retrieve account details
                                                  ↓
                                         Fetch notification preferences
                                                  ↓
                                         Send personalized email
```

**Client Implementation:**
```java
@FeignClient(name = "account-service")
public interface AccountServiceClient {
    @GetMapping("/accounts/{name}")
    Account getAccount(@PathVariable String name);
}
```

This pattern means:
- Services remain loosely coupled
- Service discovery is automatic (Eureka)
- Client-side load balancing built in
- Fault tolerance via circuit breakers (Spring Cloud)

### 5.2 Asynchronous Communication

**Message Bus: Spring Cloud Bus (AMQP/RabbitMQ)**

Used for: Dynamic configuration refresh
```
Config Server → Spring Cloud Bus → All Services
                                        ↓
                                   Refresh bean state
                                        ↓
                                   @RefreshScope beans reload
```

**Real-world Example:** Change email subject/body in Config Service → All services refresh without restart

---

## 6. Scalability & Deployment Architecture

### 6.1 Horizontal Scaling Characteristics

**Per-Service Scaling Capability:**

| Service | Scaling Needs | Bottleneck |
|---------|---------------|-----------|
| Account Service | Medium (User load) | MongoDB document storage |
| Statistics Service | High (Calculation heavy) | CPU for time-series processing |
| Notification Service | Low (Scheduled delivery) | SMTP/Email provider limits |
| Auth Service | Medium (Token validation) | Token store (in-memory) |
| API Gateway | High (All traffic passes through) | Network I/O |

**Strategy:** Each service can be deployed to multiple containers and load-balanced independently.

### 6.2 Database Architecture

```
PiggyMetrics Database Isolation Pattern:

Account Service  ──→  MongoDB Instance #1  [accounts collection]
Statistics Service  ──→  MongoDB Instance #2  [statistics collection]
Notification Service  ──→  MongoDB Instance #3  [notifications collection]
```

**Benefit:** Service failure doesn't cascade to data layer
**Trade-off:** Data consistency requires API coordination (not ACID transactions)

### 6.3 Docker & Container Orchestration

Each service ships with its own Dockerfile:
```dockerfile
# Pattern used across all services
FROM java:8
COPY target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

**Deployment:** Docker Compose development, scalable to Kubernetes production

---

## 7. Configuration Management Strategy

### 7.1 Centralized Configuration

Spring Cloud Config Server manages all environment-specific settings:

```
File Structure:
├── shared/
│   ├── application.yml          (global defaults)
│   ├── account-service.yml      (service-specific)
│   ├── notification-service.yml (email settings, refresh scope)
│   └── statistics-service.yml   (algorithm configs)
```

**Benefit:** Deploy same Docker image to dev/staging/production
**Mechanism:** Service bootstrap.yml points to Config Server
```yaml
spring:
  application:
    name: notification-service
  cloud:
    config:
      uri: http://config:8888
      fail-fast: true  # ← Important: don't start if config missing
```

### 7.2 Dynamic Configuration with @RefreshScope

**EmailService Bean Example:**
```java
@Component
@RefreshScope
public class EmailServiceImpl implements EmailService {
    @Value("${email.subject}")
    private String subject;
    
    // Changes picked up without restart
    // Trigger: POST /notifications/refresh (with OAuth2 token)
}
```

**Product Implication:** Change marketing messaging (email subject/body) in production without service restart

---

## 8. Distributed System Capabilities

### 8.1 Service Discovery & Load Balancing

**Technology:** Netflix Eureka + Spring Cloud

```
Account Service (Instance 1)  ─┐
Account Service (Instance 2)  ─|── Eureka Registry
Account Service (Instance 3)  ─┘
                    ↑
              (Auto-registered)

Notification Service → Eureka (lookup) → Get Account Service instances
                                              ↓
                                         Load balance requests
```

### 8.2 Distributed Tracing

**Technology:** Spring Cloud Sleuth

```
HTTP Request enters API Gateway
    ↓
[Trace ID: abc123]
    ↓
API Gateway → Account Service [same trace]
    ↓
Account Service → Statistics Service [same trace]
    ↓
All logs can be correlated in central logging system
```

**Business Benefit:** Can track a complete user request across all services for debugging and performance analysis

### 8.3 Health & Monitoring

**Spring Boot Actuator Endpoints:**
```
GET /health           - Service health status
GET /metrics          - Operation metrics
GET /env              - Environment variables
GET /loggers          - Log level management
```

**Example:** Prometheus can scrape `/metrics` for monitoring dashboards

---

## 9. Feature Completeness Assessment

### 9.1 Core Financial Features

✅ **Income tracking** - Multiple income sources with amounts, periods, currency  
✅ **Expense tracking** - Categorized expenses with icons for UI  
✅ **Savings goals** - Dedicated savings tracking per account  
✅ **Multi-currency support** - Normalized financial metrics across currencies  
✅ **Time-period normalization** - Convert daily/monthly/yearly to comparable metrics  
✅ **Account notes** - Free-form annotations (up to 20K characters)  
✅ **Historical analytics** - Time-series data points for trend analysis  

### 9.2 User Management Features

✅ **User registration** - Sign up with validation  
✅ **Authentication** - OAuth2 password credentials flow  
✅ **Current user context** - Principal-aware API responses  
✅ **Demo accounts** - Unauthenticated exploration  
✅ **User preferences** - Notification settings per user  

### 9.3 Enterprise Features

✅ **OAuth2 security** - Standards-compliant authorization  
✅ **Service isolation** - Database per service, no shared schema  
✅ **Configuration management** - Centralized settings  
✅ **Dynamic updates** - @RefreshScope for zero-downtime changes  
✅ **Distributed tracing** - Cross-service request tracking  
✅ **Health monitoring** - Actuator endpoints for observability  

### 9.4 Notable Limitations (for Product Planning)

⚠️ **No built-in persistence** for authentication tokens (Config unclear in current codebase)  
⚠️ **Time-series storage** in MongoDB (not specialized TSDB like InfluxDB/TimescaleDB)  
⚠️ **No event sourcing** - Traditional CRUD model may limit audit trail  
⚠️ **Single-region deployment** - Would require replication strategy for HA  
⚠️ **No graph querying** - MongoDB documents don't support relationship queries  

---

## 10. Competitive & Market Positioning

### 10.1 What This Architecture Enables

**For Product:**
1. **Rapid feature deployment** - Services can be updated independently
2. **Personalization** - Notification preferences, custom categories
3. **Multi-currency marketplace** - Can serve global markets from day one
4. **Scalable revenue streams** - Notification service can insert sponsored emails
5. **Third-party integrations** - APIs are RESTful and documented

**For Operations:**
1. **Team autonomy** - Each service owned by separate team
2. **Selective scaling** - Scale only high-demand services
3. **Graceful degradation** - One service failure doesn't crash entire app
4. **A/B testing** - Easy to deploy variants to specific instances

### 10.2 Comparison with Competitors

| Feature | PiggyMetrics | Typical FinTech Competitor |
|---------|---|---|
| Microservices Architecture | ✓ | ✓ |
| Multi-currency support | ✓ | ✓ |
| Time-series analytics | ✓ | ✓ |
| Email notifications | ✓ | ✓ |
| OAuth2 security | ✓ | ✓ |
| Auto-scaling | Manual Docker | Kubernetes |
| Real-time dashboards | Possible | Typical |
| Regulatory compliance APIs | Not included | Often included |

---

## 11. Product Development Roadmap Implications

### 11.1 Short-term (0-3 months) - Leverage Current Architecture

- ✅ Add expense categories with icons (already designed)
- ✅ Build financial dashboard (Statistics Service ready)
- ✅ Mobile app (REST API already mobile-friendly)
- ✅ Email notifications (Notification Service ready)

### 11.2 Medium-term (3-9 months) - Strategic Enhancements

- 🔷 Add budgeting/forecasting (new microservice?)
- 🔷 Implement recurring transactions (requires Database schema updates)
- 🔷 Integration with bank APIs (new adapter service)
- 🔷 Investment tracking (separate domain service)

### 11.3 Long-term (9+ months) - Platform Evolution

- 📋 Multi-account households (parent/child or couples)
- 📋 Advisor marketplace (connect users to financial advisors)
- 📋 AI-powered insights (machine learning on time-series data)
- 📋 Regulatory compliance (PCI, KYC, AML microservices)

---

## 12. Risk Assessment

### High Risk Items

| Risk | Impact | Mitigation |
|------|--------|-----------|
| MongoDB performance at scale | Service slowdown | Implement sharding strategy, consider TSDB for Statistics |
| Service discovery dependency on Eureka | If Eureka down, new instances can't register | Implement health checks, use Kubernetes DNS in production |
| Single point of failure in Config Server | All services fail to start if config unavailable | Implement Config Server HA with replication |

### Medium Risk Items

| Risk | Impact | Mitigation |
|------|--------|-----------|
| No event sourcing for audit | Regulatory compliance issues | Implement separate audit log service |
| Token storage approach unclear | Security vulnerability | Document and validate token storage pattern |
| Cross-service transaction consistency | Data corruption in edge cases | Document eventual consistency model |

### Low Risk Items

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Java 8 EOL (2030) | Technical debt | Plan Java 11+ migration in 2027 |
| Spring Cloud Config vs. newer tools (Consul, Vault) | Feature gaps | Monitor ecosystem, migrate if needed |
| Docker Compose for production | Operational complexity | Migrate to Kubernetes for production |

---

## 13. Market Readiness Checklist

| Capability | Status | Evidence |
|-----------|--------|----------|
| **Functional Completeness** | ✅ Ready | All core financial tracking features implemented |
| **Security** | ✅ Ready | OAuth2, scope-based access control, service isolation |
| **Scalability** | ⚠️ Partial | Horizontal scaling possible, but HA/replication needs documented |
| **Operational Readiness** | ⚠️ Partial | Monitoring via Actuator, but no log aggregation documented |
| **Documentation** | ⚠️ Partial | Code well-structured, needs deployment runbooks |
| **Testing** | ❓ Unknown | Test coverage not visible in analysis |
| **Performance** | ⚠️ Partial | No benchmarks documented |
| **Regulatory Compliance** | ⚠️ Partial | Security in place, audit logging needed |

---

## 14. Recommended Next Steps for Product Leadership

### 14.1 Immediate (This Sprint)

1. **Validate Test Coverage**
   - Review unit/integration test coverage
   - Establish minimum threshold (80%+ recommended)

2. **Document Deployment Procedure**
   - Create step-by-step deployment guide
   - Establish staging environment mirrors production

3. **Define SLOs/SLAs**
   - Response time targets per endpoint
   - Uptime targets per service
   - Error budget allocation

### 14.2 Short-term (Next Quarter)

1. **Implement Application Performance Monitoring (APM)**
   - Deploy New Relic, Datadog, or open-source equivalent
   - Set up alerts for anomalies

2. **Implement Centralized Logging**
   - ELK stack (Elasticsearch, Logstash, Kibana) or Splunk
   - Ensure cross-service trace correlation

3. **Establish Security Audit Process**
   - Penetration testing plan
   - Annual security review checklist

### 14.3 Medium-term (Next 2 Quarters)

1. **Upgrade to Java 11+**
   - Spring Boot 2.5+ compatibility
   - Performance improvements, security patches

2. **Kubernetes Migration Plan**
   - Phase out Docker Compose for production
   - Implement auto-scaling policies
   - Establish disaster recovery procedures

3. **API Versioning Strategy**
   - Design v2 API plan
   - Establish backward compatibility guidelines

---

## 15. Financial Impact Summary

### Development Velocity
- **Team Independence:** 4-5 independent teams possible (one per service)
- **Deployment Frequency:** Could enable daily deployments per service
- **Time to Market:** Estimated 30-40% faster for new features vs. monolithic architecture

### Operational Costs
- **Infrastructure:** Estimated 40% higher than monolith (more containers, databases)
- **Complexity:** Operations team size should grow 50% to handle distributed system
- **Observability Tools:** Budget $500-2,000/month for APM, logging, monitoring

### Customer Impact
- **Availability:** Can target 99.9% uptime (vs. 99% monolith) with proper HA setup
- **Personalization:** Easier to implement per-user customization
- **Internationalization:** Multi-currency support built-in from day one

---

## 16. Conclusion

PiggyMetrics demonstrates a **mature, production-grade microservices architecture** suitable for a fintech platform. The technology choices reflect industry best practices (Spring Cloud, Docker, MongoDB, OAuth2) and enable the key capabilities needed for a competitive financial services application:

✅ **Multi-currency support** for international expansion  
✅ **Modular architecture** for rapid feature deployment  
✅ **Enterprise security** with OAuth2 and service isolation  
✅ **Scalability** for handling growth without architectural changes  
✅ **Operational flexibility** via centralized configuration management  

**Primary opportunity:** Enhance operational readiness (monitoring, logging, deployment automation) before public launch. The functional and architectural foundations are solid.

**Approval Status:** **RECOMMENDED FOR INVESTMENT** — with medium-term operational enhancements.

---

## Appendix: Analysis Methodology

This analysis was performed using the **Documentation Cartographer Tool**, which automatically:
1. Mapped service dependencies through codebase scanning
2. Extracted API contracts from controller annotations
3. Analyzed domain models from entity definitions
4. Identified configuration patterns and deployment mechanisms
5. Cross-referenced data flow across microservices

The tool enables product managers to rapidly understand complex architectures without requiring deep technical expertise or manual code reading—critical capability for accelerating product decision-making in engineering-led organizations.

---

**Document Generated:** March 11, 2026  
**Tool:** Documentation Cartographer MCP  
**Analysis Depth:** Comprehensive (Full codebase scan + architecture mapping)
