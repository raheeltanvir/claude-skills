# Proposed Architecture: Customer Data Platform Modernization

## Background

We're migrating off our legacy on-prem Teradata warehouse to a cloud lakehouse on AWS + Databricks. Current pain points: batch-only nightly loads, no self-service access for analytics teams, and a single monolithic customer table that every team edits directly.

## Source Systems

- Legacy Teradata EDW (10 years of history, ~40TB)
- Salesforce (CRM, updated via nightly export today)
- Order management system (PostgreSQL, OLTP)
- Web clickstream events (currently written to S3 via a nightly batch job from the app servers)

## Target Platform

- Databricks Lakehouse on AWS, Unity Catalog for governance
- Medallion architecture: bronze (raw), silver (cleaned/conformed), gold (business-level aggregates)
- Delta Live Tables for the bronze → silver pipelines
- Domain teams (Marketing, Sales, Fulfillment) each own their own gold-layer tables under a data mesh model
- A separate "Customer 360" gold table combines identity from CRM, orders, and clickstream for a unified customer view, maintained by the central data platform team

## Ingestion

- Order management system: moving to CDC via Debezium → Kafka → bronze, to get near-real-time order status into the platform
- Salesforce and clickstream: staying on nightly batch for now, no immediate plan to change

## Security

- PII (name, email, phone, address) lives in the CRM and order tables
- Plan is to mask PII columns using Unity Catalog dynamic views, applied at query time, with unmasked access limited to a "PII_ACCESS" group
- No specific plan yet documented for handling GDPR-style deletion/right-to-be-forgotten requests across bronze/silver/gold copies

## MDM / Identity

- Customer 360 table will match/merge records across CRM, orders, and clickstream using email as the primary match key
- No fallback rule defined yet for records without email (e.g., guest checkout orders, anonymous clickstream)
- No documented process for what happens when Marketing's local customer record disagrees with the central Customer 360 record

## Migration Plan

- Run new pipelines in parallel with Teradata for 4 weeks
- Cut over reporting to the new platform once Finance signs off on number parity for the top 20 reports
- No formal rollback plan documented if discrepancies are found after cutover
- Teradata will be decommissioned 60 days after cutover

## Timeline

Target go-live in 5 months. Team is 6 engineers plus 2 analytics engineers embedded in domain teams.
