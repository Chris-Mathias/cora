# Cora: A Multi-Tenant ERP System

## About The Project

**Cora** is a multi-tenant Enterprise Resource Planning (ERP) system being developed with **Django**. The system is designed with a **service-oriented architecture**, starting with a well-defined data model layer.

The **multi-tenant design** ensures data isolation, allowing multiple organizations to use a single deployed instance securely.

---

## Current Project Status

**Phase:** Initial Data Modeling

The project is in the early stages of development. The core data models for **tenants, users, products**, and **customers** have been defined and implemented using Django's ORM.

The following components have not yet been developed:

- **Business Logic Layer**: Views, serializers, and complex business rule validations.
- **API Layer**: URL endpoints for exposing the models' functionalities.
- **Core Modules**: Models for inventory, finance, sales, and production.

---

## Implemented Data Models

### Multi-Tenant Architecture

- **Tenant Model**: Central model of the system. All other data is associated with a specific tenant.
- **TenantUser Model**: A through-model that links a User to a Tenant and Role.

### User & Access Management (RBAC)

- **Custom User Model**: Uses email for authentication (instead of username).
- **Role Model**:
  - Implements **Role-Based Access Control** (RBAC).
  - Supports both **global roles** (`tenant=None`) and **tenant-specific roles**.
  - Linked to Django’s native **Permission model** for fine-grained access control.

### Product Management

- **Product Model**: Supports multiple product structures:
  - **Simple Products**: Standard single-item products.
  - **Variant Products**: Self-referencing parent key to define product variants (e.g., T-shirt with sizes/colors).
  - **Composite Products**: Many-to-many to self, allowing bundles or kits.
- **Supporting Models**:
  - `ProductCategory`
  - `ProductBrand`
  - `Attribute` / `AttributeValue`

### Customer Management

- **Customer Model**: Manages customer records per tenant.

### Location Module

- `Country`
- `State`
- `City`

---

## Roadmap: What's Next

### 1. Core Module Modeling

- [ ] Inventory Management
  - [ ] Stock Movement (entry, exit, transfers)
  - [ ] Inventory Adjustment & Stocktaking

- [ ] Financial Module
  - [ ] Accounts Payable / Receivable
  - [ ] Cash Flow Transactions

- [ ] Sales Module
  - [ ] Sales Order / Sales Order Item
  - [ ] Invoicing Models

- [ ] Production Module
  - [ ] Production Orders Model

- [ ] Purchase Module
  - [ ] Purchase Order Model

---

### 2. API Layer Implementation

- [ ] Views / ViewSets
- [ ] Serializers
- [ ] URL Endpoints
- [ ] Business Logic and Validations

---

### 3. Additional Features

- [ ] Dashboard & Reporting
  - [ ] KPI Aggregation
  - [ ] Sales & Inventory Reports

---

## Technology Stack

- **Backend**: Python, Django  
- **Database**: *(To be specified — e.g., PostgreSQL or MySQL)*

---

## Getting Started

Instructions on how to set up the project locally will be added soon.
