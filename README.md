# Cora: A Multi-Tenant ERP System

## About The Project

**Cora** is a multi-tenant Enterprise Resource Planning (ERP) system being developed with **Django**. The system is designed with a **service-oriented architecture**, starting with a well-defined data model layer.

The **multi-tenant design** ensures data isolation, allowing multiple organizations to use a single deployed instance securely.

---

## Current Project Status

**Phase:** Core Data Modeling Complete & Service Layer Implementation in Progress

The project has completed its initial data modeling phase. All core modules have been modeled using Django's ORM. The development is now focused on implementing the business logic within a dedicated service layer.

The following components have not yet been developed:

- **API Layer**: URL endpoints, Views/ViewSets, and Serializers for exposing the system's functionalities.
- **Comprehensive Business Logic**: While foundational services are being built, most cross-module business rules are still pending.
- **User Interface (UI)**: No frontend has been developed yet.

---

## Implemented Modules

### Data Models

The complete database schema has been defined for the following modules:

- Multi-Tenant Architecture: Tenant, TenantUser
- User & Access Management (RBAC): Custom User, Role (global and tenant-specific) linked to Django Permission.
- Product Management: Product (simple, variant, composite), ProductCategory, ProductBrand, Attribute, AttributeValue.
- Customer Management: Customer.
- Supplier Management: Supplier.
- Location Module: Country, State, City.
- Sales Module: SaleOrder, SaleOrderItem, SaleOrderStatus, SaleOrderHistory.
- Purchase Module: PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus.
- Production Module: ProductionOrder, ProductionStage, ProductionStageHistory.
- Inventory Module: StockMovement (centralized ledger), StockEntry, StockAdjustment, and their respective items and reasons.
- Financial Module: AccountPayable, AccountReceivable, PaymentTransaction, CashFlow, CompanyAccount, FinancialCategory, FinancialStatus.

### Service Layer

A service-oriented architecture is being implemented to encapsulate business logic. The following services have been developed:

- inventory.services: Centralizes all stock operations. Provides functions to create stock entries and adjustments, ensuring all changes are atomic and correctly registered in StockMovement.

## Roadmap: What's Next

1. Core Module Modeling  
   [x] Inventory Management  
   [x] Financial Module  
   [x] Sales Module  
   [x] Production Module  
   [x] Purchase & Supplier Module

2. Service Layer Implementation  
   [x] Implement inventory_service.  
   [ ] Implement sale_order_service.  
   [ ] Implement financial_service for payment processing.  
   [ ] Implement purchase_service for purchase order lifecycle.  
   [ ] Implement production_service for production order lifecycle.

3. API Layer Implementation  
   [ ] Implement Views / ViewSets for all models.  
   [ ] Implement Serializers for data representation.  
   [ ] Define URL Endpoints.

4. Additional Features  
   [ ] Dashboard & Reporting:  
   [ ] KPI Aggregation  
   [ ] Sales & Inventory Reports

## Technology Stack

Backend: Python, Django  
Database: (To be specified — e.g., PostgreSQL or MySQL)

## Getting Started

Instructions on how to set up the project locally will be added soon.
