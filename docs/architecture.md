# Architecture

Campaign Copilot is organized as a small multi-service application with shared infrastructure.

## Services

### CRM Service

Owns future CRM-facing APIs, models, repositories, schemas, and application services.

### Channel Simulator Service

Owns future marketing channel simulation APIs, models, repositories, schemas, and application services.

### Streamlit App

Provides the user-facing frontend. It should communicate with backend services over HTTP once business workflows are added.

## Shared Layer

The `shared/` package contains infrastructure that can be safely reused by services:

- Configuration loading
- Database engine and session factory
- SQLAlchemy declarative base
- Common ORM mixins
- AI provider configuration helpers

## Clean Architecture Boundaries

- Routers should translate HTTP requests into application service calls.
- Services should coordinate use cases.
- Repositories should own persistence access.
- Models should define database persistence shape.
- Schemas should define external request and response contracts.
- Utilities should remain small and service-local.

No business logic is included in this scaffold.
