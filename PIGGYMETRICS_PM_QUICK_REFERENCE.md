# PiggyMetrics: PM Quick Reference & Implementation Checklist
**Purpose:** Tactical guide for product managers implementing features  
**Format:** Quick lookup tables, decision trees, checklists  
**Generated:** March 11, 2026 (via Documentation Cartographer)

---

## Quick Reference: API Endpoints Available Today

### Account Service Endpoints

| Endpoint | Method | Auth? | Purpose | Response |
|----------|--------|-------|---------|----------|
| `/accounts/{name}` | GET | Optional | Fetch any account (if authorized) | Account object |
| `/accounts/current` | GET | ✅ Required | Get own account | Account object |
| `/accounts/current` | PUT | ✅ Required | Update own account | 200 OK |
| `/accounts/` | POST | ❌ None | Register new account | Account object |
| `/accounts/demo` | GET | ❌ None | Get demo account | Pre-filled Account |

### Statistics Service Endpoints

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/statistics/{account}` | GET | Get account trends | Time-series datapoints |
| `/statistics/current` | GET | Get own trends | Requires authentication |
| `/statistics/demo` | GET | Demo statistics | Unauthenticated |
| `/statistics/{account}` | PUT | Record transaction | Backend use |

### Notification Service

| Endpoint | Method | Purpose | Notes |
|----------|--------|---------|-------|
| `/notifications/settings/current` | GET | Get preferences | Requires auth |
| `/notifications/settings/current` | PUT | Update preferences | Requires auth |
| `/notifications/refresh` | POST | Reload config | Admin use |

---

## Feature Feasibility Matrix

### New Features: Can We Build This?

**Recurring Income**
```
Complexity:  ██░░░░░░░ LOW
Effort:      2-3 weeks
Blocker:     None - add to Item model
Timeline:    Month 3-4
```

**Budget Alerts**
```
Complexity:  ███░░░░░░ LOW-MEDIUM
Effort:      3-4 weeks  
Blocker:     Notification Service scheduler
Timeline:    Month 3-4
```

**Category Automation**
```
Complexity:  ████░░░░░ MEDIUM
Effort:      4-5 weeks
Blocker:     ML model training, integration test
Timeline:    Month 5-6
```

**Bank Integration**
```
Complexity:  ███████░░ HIGH
Effort:      10-12 weeks
Blocker:     Plaid SDK, data mapping, reconciliation
Timeline:    Month 8-10
```

**Investment Tracking**
```
Complexity:  ██████░░░ MEDIUM-HIGH
Effort:      8-10 weeks
Blocker:     New service architecture, price feeds
Timeline:    Month 9-11
```

**Advisor Marketplace**
```
Complexity:  ███████░░ HIGH
Effort:      12-14 weeks
Blocker:     Payments, KYC verification, escrow
Timeline:    Month 10-14
```

---

## Implementation Decision Tree

### "I Have a Feature Idea - Can We Build It?"

```
┌─────────────────────────────────────────────────────────┐
│ Does this feature use existing data (Account fields)?   │
└─────────────────────────┬───────────────────────────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
              YES                  NO
                │                   │
                ▼                   ▼
        ┌──────────────────┐  ┌──────────────────────┐
        │Can add to current│  │Requires new data or  │
        │   Item model?    │  │     new service?     │
        └┬─────────────────┘  └──────────┬───────────┘
         │                               │
        YES                             YES
         │                               │
         ▼                               ▼
    EASY (2-3 wks)              MEDIUM (4-8 wks)
    ✅ Add field to schema      ⚠️ New microservice
    ✅ Update validators         ⚠️ API contracts
    ✅ Expose via REST API      ⚠️ Data persistence
    
    Example:                    Example:
    - Recurring rule            - Bank integration
    - Budget category           - Investment service
    - Tax status                - Advisor matching
    
         │                               │
         └───────────┬───────────────────┘
                     │
                     ▼
          Do we have team capacity?
                     │
          ┌──────────┴──────────┐
          │                     │
         YES                   NO
          │                     │
          ▼                     ▼
      PROCEED              PRIORITIZE
      Add to sprint        Add to roadmap (Q2/Q3)
```

---

## Database Model Extension Guide

### Current Account Schema

```javascript
{
  _id: ObjectId,
  name: String (unique),
  lastSeen: Date,
  incomes: [Item],      // <-- Can extend Item
  expenses: [Item],     // <-- Can extend Item  
  saving: {             // <-- Can extend Saving
    amount: BigDecimal,
    currency: String,
    period: String
  },
  note: String
}
```

### Common Extensions

#### ADD: Recurring Transaction Support
```javascript
// Add to Item model:
{
  title: String,
  amount: BigDecimal,
  currency: String,
  period: String,        // EXISTING
  icon: String,
  
  // NEW FIELDS:
  recurring: Boolean,           // ✅ Add
  recurrenceRule: String,       // ✅ Add (RRULE format)
  recurrenceEndDate: Date,      // ✅ Add
  nextOccurrence: Date          // ✅ Add (for sorting)
}
```
**Effort:** 2 weeks | **Risk:** Low | **Database migration:** Simple

#### ADD: Expense Categories
```javascript
// ADD new field to Item:
{
  // ... existing fields ...
  category: String,     // ✅ Add (food, transport, entertainment)
  subcategory: String   // ✅ Add (for detailed budgeting)
}
```
**Effort:** 1 week | **Risk:** Very Low | **Indexing needed:** Yes

#### ADD: Budget Tracking
```javascript
// ADD to Account model:
{
  // ... existing fields ...
  budgets: [{           // ✅ Add new array
    category: String,
    limit: BigDecimal,
    period: String (MONTHLY/YEARLY),
    currency: String,
    alertThreshold: Number (e.g., 0.8 = alert at 80%)
  }]
}
```
**Effort:** 1.5 weeks | **Risk:** Low | **Complexity:** Medium

#### ADD: Financial Goals
```javascript
// ADD to Account model:
{
  // ... existing fields ...
  goals: [{             // ✅ Add new array
    name: String (e.g., "Emergency Fund"),
    targetAmount: BigDecimal,
    currentAmount: BigDecimal,
    currency: String,
    deadline: Date,
    priority: String (HIGH, MEDIUM, LOW)
  }]
}
```
**Effort:** 1 week | **Risk:** Very Low | **Revenue impact:** High

---

## Service Extension Guide

### When to Create a New Microservice

**Good Candidates for New Service:**
- ✅ Has its own database
- ✅ Different scaling requirements
- ✅ Different security model
- ✅ Will be owned by separate team
- ✅ Can fail independently

**New Service Template:**
```
new-service/
├── src/main/java/.../
│   ├── NewServiceApplication.java
│   ├── controller/
│   ├── domain/
│   ├── repository/
│   ├── service/
│   └── config/
├── src/main/resources/
│   └── bootstrap.yml (Config Server reference)
├── Dockerfile
└── pom.xml (copy from existing service)
```

### Examples: When to Add Service vs. Extend Existing

| Feature | Add to Service | New Service | Rationale |
|---------|---|---|---|
| Budget alerts | Account | No | Same data, same ownership |
| Bank sync | No | ✅ bank-connector | Different scaling, separate team |
| Investment tracking | No | ✅ investment | Separate domain, different DB |
| Advisor matching | No | ✅ advisor | High load, separate payment logic |
| ML insights | No | ✅ ml-processor | Compute intensive, async |
| Notification templates | Notification | No | Same service, different config |

---

## Release Checklist Template

### Before Launching New Feature

**Development Complete**
- [ ] Code reviewed (2+ reviewers)
- [ ] Unit tests passing (80%+ coverage)
- [ ] Integration tests passing
- [ ] All PR comments resolved

**Testing**
- [ ] QA sign-off on test cases
- [ ] Staging environment tested
- [ ] Load test on expected traffic
- [ ] Manual end-to-end test (production data copy)

**Documentation**
- [ ] API documentation updated
- [ ] Database migration documented
- [ ] Configuration changes listed
- [ ] Rollback procedure documented

**Operations**
- [ ] Monitoring alerts configured
- [ ] Health check endpoints verified
- [ ] Logs checked in aggregation tool
- [ ] Runbook created for incidents

**Security & Compliance**
- [ ] Security audit (if handling new data)
- [ ] Privacy impact assessment (if new PII)
- [ ] Dependency scan (vulnerabilities)
- [ ] Rate limiting configured

**Deployment**
- [ ] Staging deployed 24h test
- [ ] Database backups verified
- [ ] Feature flags configured (for gradual rollout)
- [ ] On-call rotation established

**Post-Launch**
- [ ] Monitor error rates (< 0.1%)
- [ ] Monitor latency (p95 < SLO)
- [ ] Monitor user adoption
- [ ] Stay on-call for 48 hours

---

## Metrics Dashboard for PMs

### What to Monitor Post-Launch

**Daily Standup Metrics**
```
User Signups:             ##  (target: 50-100/day at launch)
Feature Adoption Rate:    ##  (target: 30-40% for new features)
Error Rate:               ##  (target: < 0.1%)
API Latency (p95):        ##  (target: < 300ms)
User Retention (DAU):     ##  (target: > 40% at day 7)
```

**Weekly Review Metrics**
```
Churn Rate:               ##  (target: < 5%/month)
Feature Feedback Score:   ##  (NPS: target > 0)
Critical Bugs:            ##  (target: 0)
Customer Support Tickets: ##  (target: < 50/week early)
```

**Monthly Business Review Metrics**
```
Monthly Active Users:     ##
Premium Conversion Rate:  ##  (target: 5-10% eventually)
Monthly Recurring Revenue: $ ##
Customer Acquisition Cost: $ ##
Customer Lifetime Value:  $ ##
```

---

## Common PM Questions: Answered by Architecture

### Q: Can we A/B test a new UI for one user segment?
**A:** Yes. The API is stateless - you can serve different frontends pointing to same backend. No code change needed.

### Q: What if we need to change email templates without downtime?
**A:** The Notification Service uses @RefreshScope. Update Config Server → Call `/refresh` → No restart needed.

### Q: Can one service go down without breaking the app?
**A:** Partially. If Account Service is down, users can't see data but Statistics still works. Good design = graceful degradation.

### Q: How long to scale to 100K users?
**A:** With this architecture, scaling is mostly ops (add Docker containers). Code doesn't need changes. ETA: handle 2-3x traffic by adding 2-3x containers.

### Q: Can we support multiple currencies from Day 1?
**A:** Yes, it's already in the schema. No code changes needed for basic support.

### Q: How do we A/B test email subject lines?
**A:** Store variant in Config Server. Deploy to 50% of users. Measure conversion. Switch winner to 100%.

### Q: What if a feature flops? How hard is rollback?
**A:** If feature is in new service = delete service (clean). If in existing service = toggle via feature flag (safest).

---

## Team Allocation Guide

### Suggested Team Structure (When Scaling)

**Team 1: Account Service** (5 people)
- Owner: Backend Lead #1
- Focus: User data, income/expense tracking, account settings
- Planning: 3-week sprints
- Examples: Budget alerts, recurring transactions, categories

**Team 2: Statistics Service** (4 people)
- Owner: Backend Lead #2
- Focus: Time-series analytics, reporting, dashboards
- Planning: 3-week sprints
- Examples: Trend calculations, financial insights, projections

**Team 3: Notification Service** (3 people)
- Owner: Backend Lead #3
- Focus: Email, webhooks, messaging
- Planning: 3-week sprints
- Examples: Alert system, notification preferences, templates

**Team 4: New Capabilities** (6 people)
- Bank integration (2)
- Investment service (2)
- ML insights (2)

**Team 5: DevOps/Infrastructure** (3 people)
- Kubernetes, monitoring, databases
- CI/CD pipelines
- Production support

**Team 6: Frontend** (4-6 people)
- Web dashboard
- Mobile apps (separate iOS/Android)
- Responsive design

---

## Competitive Comparison Cards

### vs. Mint/YNAB (Legacy Incumbents)

| Aspect | PiggyMetrics | Competitors |
|--------|---|---|
| Multi-currency foundation | ✅ Built-in | ⚠️ Retrofit |
| API for partners | ✅ REST ready | ⚠️ Limited |
| Advisor marketplace | ✅ Possible | ⚠️ Hard to add |
| International scaling | ✅ Easy | ⚠️ Hard |
| Feature velocity | ✅ Fast (microservices) | ⚠️ Slow (monolith) |

### vs. Plaid (API-first Fintech)

| Aspect | PiggyMetrics | Plaid |
|--------|---|---|
| Bank connectivity | 🔷 Planned | ✅ Core business |
| User account | ✅ Can build | ❌ Not core |
| Analytics | ✅ Can build | 🔷 Research |
| Mobile-first | 🔷 After web | ✅ Native |
| B2B licensing | ✅ Possible | ✅ Core |

### vs. Modern Fintech (Chime, Square)

| Aspect | PiggyMetrics | Modern Fintech |
|--------|---|---|
| Microservices | ✅ Day 1 | ✅ Yes |
| Scalability | ✅ Yes | ✅ Yes |
| Security | ✅ OAuth2 | ✅ Enterprise |
| Time-to-scale | ✅ 6-12 mo | ⚠️ 18-24 mo |

---

## Pricing Strategy Options

### Aligned with Architecture

**Option A: Freemium (Recommended)**
```
Free Tier:
  - Account tracking
  - Basic analytics
  - Email reminders
  - Unlimited transactions

Premium Tier ($9.99/mo):
  - Advanced analytics
  - Custom budgets per category
  - Savings goals
  - Ad-free experience
  - Email support

Pro Tier ($19.99/mo):
  - Bank integration
  - Investment tracking
  - Financial advisor directory
  - Priority support

Enterprise Custom:
  - White-label
  - API access
  - Dedicated support
```

**Rationale:** Architecture supports all tiers - different feature flags point to different services.

---

## Quick Decision Framework

### "We Want to Add [FEATURE]. What's the Plan?"

```
Recurring Transactions?
  └─→ Team: Account Service
      Timeline: 3 weeks
      Effort: Medium
      Risk: Low
      Launch: Month 3-4

Budget Alerts?
  └─→ Team: Notification Service
      Timeline: 4 weeks
      Effort: Low-Medium
      Risk: Low
      Launch: Month 3-4

Bank Integration?
  └─→ Team: New Team (bank-connector-service)
      Timeline: 12 weeks
      Effort: High
      Risk: Medium
      Launch: Month 8-10

AI Recommendations?
  └─→ Team: New Team (ml-processor-service)
      Timeline: 10 weeks
      Effort: High
      Risk: Medium
      Launch: Month 7-9

Advisor Marketplace?
  └─→ Team: New Team (3 services + payments)
      Timeline: 14 weeks
      Effort: Very High
      Risk: High
      Launch: Month 10-14
```

---

## Success Metrics to Track

### For Each Launch Phase

**PHASE 1: Initial Launch (Months 1-4)**
```
✓ User acquisition: 5K-10K users
✓ DAU: 30-40% of registered
✓ Core feature adoption: 80%+ use income/expense tracking
✓ Error rate: < 0.5%
✓ API latency: < 250ms p95
```

**PHASE 2: Feature Expansion (Months 5-8)**
```
✓ Premium conversion: 3-5%
✓ Feature adoption: 50%+ use new features
✓ Churn rate: < 5%/month
✓ NPS score: > 30
✓ Organic growth: 20%+ of new users
```

**PHASE 3: Platform Play (Months 9-12)**
```
✓ Advisor marketplace: $10K+ GMV/month
✓ Mobile MAU: 80% of total
✓ Bank-connected accounts: 30% of users
✓ MRR: $50K+
✓ Market penetration: Top 10 in category
```

---

## Final Recommendation

This architecture is ready for rapid product evolution. The PM team can:
- Launch MVP in 4-6 weeks (frontend dev)
- Add 2-3 features monthly once launched
- Scale to 1M+ users without architectural changes
- Pivot quickly to new revenue streams

**Most important:** Focus on user acquisition and retention. The technology is solid. Success depends on marketing and product-market fit.

---

**Document Generated:** March 11, 2026  
**Tool:** Documentation Cartographer MCP  
**Version:** 1.0  
**Audience:** Product and Program Managers
