import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from pydantic import BaseModel
from typing import List, Optional
import bcrypt

app = FastAPI(title="Uncle Joe's API", docs_url="/docs")

# CORS Configuration - Allowing all origins for now as the frontend URL is TBD
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = bigquery.Client(project="mgmt-545-gp")

# Data Models
class Location(BaseModel):
    id: str
    city: Optional[str] = None
    state: Optional[str] = None
    address_one: Optional[str] = None
    open_for_business: Optional[bool] = None
    wifi: Optional[bool] = None
    drive_thru: Optional[bool] = None
    door_dash: Optional[bool] = None

    hours_monday_open: Optional[int] = None
    hours_monday_close: Optional[int] = None
    hours_tuesday_open: Optional[int] = None
    hours_tuesday_close: Optional[int] = None
    hours_wednesday_open: Optional[int] = None
    hours_wednesday_close: Optional[int] = None
    hours_thursday_open: Optional[int] = None
    hours_thursday_close: Optional[int] = None
    hours_friday_open: Optional[int] = None
    hours_friday_close: Optional[int] = None
    hours_saturday_open: Optional[int] = None
    hours_saturday_close: Optional[int] = None
    hours_sunday_open: Optional[int] = None
    hours_sunday_close: Optional[int] = None

class MenuItem(BaseModel):
    id: str
    name: Optional[str] = None
    category: Optional[str] = None
    size: Optional[str] = None
    calories: Optional[int] = None
    price: Optional[float] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    authenticated: bool
    member_id: str
    name: str
    email: str
    home_store: Optional[str] = None
    home_store_city: Optional[str] = None
    home_store_state: Optional[str] = None
    home_store_address: Optional[str] = None
    phone_number: Optional[str] = None

class OrderItem(BaseModel):
    item_name: Optional[str] = None
    size: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None

class MemberOrder(BaseModel):
    order_id: str
    order_date: Optional[str] = None
    store_city: Optional[str] = None
    store_state: Optional[str] = None
    order_total: Optional[float] = None
    items: List[OrderItem] = []

class PointsResponse(BaseModel):
    member_id: str
    points_balance: int

class PointsHistoryItem(BaseModel):
    order_id: str
    order_date: Optional[str] = None
    order_total: Optional[float] = None
    points_earned: int

@app.get("/locations", response_model=List[Location])
def get_locations(
    state: str = None,
    city: str = None,
    open_for_business: bool = None,
    limit: int = 50,
    offset: int = 0,
):
    query = """
SELECT 
  id,
  city,
  state,
  address_one,
  open_for_business,
  wifi,
  drive_thru,
  door_dash,
  hours_monday_open,
  hours_monday_close,
  hours_tuesday_open,
  hours_tuesday_close,
  hours_wednesday_open,
  hours_wednesday_close,
  hours_thursday_open,
  hours_thursday_close,
  hours_friday_open,
  hours_friday_close,
  hours_saturday_open,
  hours_saturday_close,
  hours_sunday_open,
  hours_sunday_close
FROM `mgmt-545-gp.uncle_joes.locations`
WHERE 1=1
"""
    params = []
    if state:
        query += " AND LOWER(state) = LOWER(@state)"
        params.append(bigquery.ScalarQueryParameter("state", "STRING", state))
    if city:
        query += " AND LOWER(city) = LOWER(@city)"
        params.append(bigquery.ScalarQueryParameter("city", "STRING", city))
    if open_for_business is not None:
        query += " AND open_for_business = @open_for_business"
        params.append(bigquery.ScalarQueryParameter("open_for_business", "BOOL", open_for_business))
    query += " ORDER BY state, city LIMIT @limit OFFSET @offset"
    params.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))
    params.append(bigquery.ScalarQueryParameter("offset", "INT64", offset))
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    rows = client.query(query, job_config=job_config).result()
    return [dict(row) for row in rows]

@app.get("/locations/{location_id}", response_model=Location)
def get_location(location_id: str):
    query = """
    SELECT 
      id,
      city,
      state,
      address_one,
      open_for_business,
      hours_monday_open,
      hours_monday_close,
      hours_tuesday_open,
      hours_tuesday_close,
      hours_wednesday_open,
      hours_wednesday_close,
      hours_thursday_open,
      hours_thursday_close,
      hours_friday_open,
      hours_friday_close,
      hours_saturday_open,
      hours_saturday_close,
      hours_sunday_open,
      hours_sunday_close
    FROM `mgmt-545-gp.uncle_joes.locations`
    WHERE id = @id
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", location_id)])
    rows = list(client.query(query, job_config=job_config).result())
    if not rows:
        raise HTTPException(status_code=404, detail="Location not found")
    return dict(rows[0])

@app.get("/menu", response_model=List[MenuItem])
def get_menu():
    query = """
    SELECT 
      id,
      name,
      category,
      size,
      calories,
      CAST(price AS FLOAT64) AS price
    FROM `mgmt-545-gp.uncle_joes.menu_items`
    """
    rows = client.query(query).result()
    return [dict(row) for row in rows]

@app.get("/menu/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: str):
    query = """
    SELECT 
      id,
      name,
      category,
      size,
      calories,
      CAST(price AS FLOAT64) AS price
    FROM `mgmt-545-gp.uncle_joes.menu_items`
    WHERE id = @id
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", item_id)])
    rows = list(client.query(query, job_config=job_config).result())
    if not rows:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict(rows[0])

@app.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    query = """
    SELECT
        m.string_field_0 AS id,
        m.string_field_1 AS first_name,
        m.string_field_2 AS last_name,
        m.string_field_3 AS email,
        m.string_field_4 AS phone_number,
        m.string_field_5 AS home_store,
        m.string_field_6 AS password,
        l.city AS home_store_city,
        l.state AS home_store_state,
        l.address_one AS home_store_address
    FROM `mgmt-545-gp.uncle_joes.members` m
        LEFT JOIN `mgmt-545-gp.uncle_joes.locations` l
    ON m.string_field_5 = l.id
        WHERE LOWER(m.string_field_3) = LOWER(@email)
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", body.email)
        ]
    )

    rows = list(client.query(query, job_config=job_config).result())

    if not rows:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    row = rows[0]
    submitted_password = body.password.encode("utf-8")
    stored_hash = row["password"].encode("utf-8")

    if not bcrypt.checkpw(submitted_password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "authenticated": True,
        "member_id": row["id"],
        "name": f"{row['first_name']} {row['last_name']}",
        "email": row["email"],
        "phone_number": row["phone_number"],
        "home_store": row["home_store"],
        "home_store_city": row["home_store_city"],
        "home_store_state": row["home_store_state"],
        "home_store_address": row["home_store_address"],
    }

@app.get("/members/{member_id}/orders", response_model=List[MemberOrder])
def get_member_orders(member_id: str):
    query = """
    SELECT
      o.order_id,
      CAST(o.order_date AS STRING) AS order_date,
      l.city AS store_city,
      l.state AS store_state,
      CAST(o.order_total AS FLOAT64) AS order_total,
      oi.item_name,
      oi.size,
      oi.quantity,
      CAST(oi.price AS FLOAT64) AS price
    FROM `mgmt-545-gp.uncle_joes.orders` o
    LEFT JOIN `mgmt-545-gp.uncle_joes.locations` l
      ON o.store_id = l.id
    LEFT JOIN `mgmt-545-gp.uncle_joes.order_items` oi
      ON o.order_id = oi.order_id
    WHERE o.member_id = @member_id
    ORDER BY o.order_date DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("member_id", "STRING", member_id)
        ]
    )

    rows = list(client.query(query, job_config=job_config).result())

    orders = {}

    for row in rows:
        order_id = row["order_id"]

        if order_id not in orders:
            orders[order_id] = {
                "order_id": order_id,
                "order_date": row["order_date"],
                "store_city": row["store_city"],
                "store_state": row["store_state"],
                "order_total": row["order_total"],
                "items": [],
            }

        if row["item_name"] is not None:
            orders[order_id]["items"].append({
                "item_name": row["item_name"],
                "size": row["size"],
                "quantity": row["quantity"],
                "price": row["price"],
            })

    return list(orders.values())

@app.get("/members/{member_id}/points", response_model=PointsResponse)
def get_member_points(member_id: str):
    query = """
    SELECT
      COALESCE(SUM(FLOOR(CAST(order_total AS FLOAT64))), 0) AS points_balance
    FROM `mgmt-545-gp.uncle_joes.orders`
    WHERE member_id = @member_id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("member_id", "STRING", member_id)
        ]
    )

    rows = list(client.query(query, job_config=job_config).result())
    points = int(rows[0]["points_balance"]) if rows else 0

    return {
        "member_id": member_id,
        "points_balance": points,
    }

@app.get("/members/{member_id}/points/history", response_model=List[PointsHistoryItem])
def get_member_points_history(member_id: str):
    query = """
    SELECT
      order_id,
      CAST(order_date AS STRING) AS order_date,
      CAST(order_total AS FLOAT64) AS order_total,
      CAST(FLOOR(CAST(order_total AS FLOAT64)) AS INT64) AS points_earned
    FROM `mgmt-545-gp.uncle_joes.orders`
    WHERE member_id = @member_id
    ORDER BY order_date DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("member_id", "STRING", member_id)
        ]
    )

    rows = client.query(query, job_config=job_config).result()
    return [dict(row) for row in rows]