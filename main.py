import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from pydantic import BaseModel
from typing import List, Optional

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
    city: str
    state: str
    address_one: str
    open_for_business: bool

class MenuItem(BaseModel):
    id: str
    name: str
    category: str
    price: float

@app.get("/locations", response_model=List[Location])
def get_locations():
    query = "SELECT id, city, state, address_one, open_for_business FROM `mgmt-545-gp.your_dataset.locations`"
    rows = client.query(query).result()
    return [dict(row) for row in rows]

@app.get("/locations/{location_id}", response_model=Location)
def get_location(location_id: str):
    query = f"SELECT id, city, state, address_one, open_for_business FROM `mgmt-545-gp.your_dataset.locations` WHERE id = @id"
    job_config = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", location_id)])
    rows = list(client.query(query, job_config=job_config).result())
    if not rows:
        raise HTTPException(status_code=404, detail="Location not found")
    return dict(rows[0])

@app.get("/menu", response_model=List[MenuItem])
def get_menu():
    query = "SELECT id, name, category, CAST(price AS FLOAT64) as price FROM `mgmt-545-gp.your_dataset.menu_items`"
    rows = client.query(query).result()
    return [dict(row) for row in rows]

@app.get("/menu/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: str):
    query = f"SELECT id, name, category, CAST(price AS FLOAT64) as price FROM `mgmt-545-gp.your_dataset.menu_items` WHERE id = @id"
    job_config = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", item_id)])
    rows = list(client.query(query, job_config=job_config).result())
    if not rows:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict(rows[0])
