# uncles-joes-api
# Uncle Joe’s Coffee Company – Backend API

## Overview
This repository contains the backend API for Uncle Joe’s Coffee Company internal pilot application.

The backend is built with **FastAPI** and deployed as a standalone service on **Google Cloud Run**. It connects directly to **Google BigQuery**, which serves as the system of record for all company data.

The API is responsible for exposing structured data to the frontend application via REST endpoints.

---

## System Architecture

This application follows a cloud-native, separated architecture:

User → Frontend (Cloud Run) → FastAPI Backend (Cloud Run) → BigQuery

- **BigQuery**: Primary data warehouse (historical company data)
- **FastAPI Backend**: Business logic + data access layer
- **Frontend**: Independent client application consuming REST APIs
- **Cloud Run**: Deployment layer for both services

---

## Tech Stack
- FastAPI (Python)
- Google BigQuery
- Poetry
- Docker
- Google Cloud Run

---

## Data Model

The backend queries the following BigQuery tables:

- `locations`
- `menu_items`
- `members`
- `orders`
- `order_items`

### Key Relationships
- `members.home_store → locations.id`
- `orders.member_id → members.id`
- `orders.store_id → locations.id`
- `order_items.order_id → orders.order_id`
- `order_items.menu_item_id → menu_items.id`

---

## API Endpoints

### Public
- `GET /menu` → Retrieve all menu items  
- `GET /locations` → Retrieve all store locations  

### Authentication
- `POST /login` → Authenticate Coffee Club member  

### Member Data (Authenticated)
- `GET /orders/{member_id}` → Retrieve full order history with line items  
- `GET /points/{member_id}` → Calculate and return loyalty points  

---

## Loyalty Points Logic
Loyalty points are computed dynamically from order history:

- 1 point per whole dollar spent.
- Values are rounded down per order.  

Example:
- $15.89 → 15 points  

Total points = sum of all order-level points per member.

---

## Running Locally
```bash
git clone https://github.com/YOUR-ORG/uncle-joes-api.git
cd uncle-joes-api
poetry install
poetry run uvicorn app.main:app --reload
```

## The API is containerized with Docker and deployed to Google Cloud Run as a stateless backend service connected to BigQuery.

Notes
All Coffee Club members share password: Coffee123!
This is a read-first system (no payments implemented)

.
