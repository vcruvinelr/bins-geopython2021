from typing import Optional, Dict, Any
from fastapi import FastAPI
import geojson
import psycopg2
import json
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = psycopg2.connect(dbname="geoapp", user="geoapp", password="geoapp")


class Hexagon(BaseModel):
    geometry: Dict[Any, Any]
    size: float


@app.post("/")
def read_root(hexagon: Hexagon):
    hex_results = []
    size = (hexagon.size/100)
    with conn.cursor() as c:

        c.execute('''
        SELECT ST_AsGeoJSON(hex.geom)
        FROM ST_HexagonGrid({size}, ST_GeomFromGeoJSON('{geojson}')) AS hex
        WHERE ST_Intersects(ST_GeomFromGeoJSON('{geojson}'), hex.geom)
        '''.format(geojson=geojson.dumps(hexagon.geometry["features"][0]["geometry"]), size=size))

        # 1 = 100km
        # 0.1 = 10km
        # 0.01 = 1km

        for row in c.fetchall():
            hex_results.append(row[0])

    return hex_results


@app.get("/points")
def get_points():
    points = []
    with conn.cursor() as c:

        c.execute('''
        SELECT ST_AsGeoJSON(geom) FROM points
        ''')

        for row in c.fetchall():
            points.append(row[0])
    
    return points

@app.get("/get_count")
def get_count():
    counts = []
    with conn.cursor() as c:

        c.execute('''
        SELECT COUNT(*), ST_AsGeoJSON(hexes.geom)
            FROM
                ST_HexagonGrid(
                    0.1,
                    ST_SetSRID(ST_EstimatedExtent('points', 'geom'), 4326)
                ) AS hexes
                INNER JOIN
                points AS pts
                ON ST_Intersects(pts.geom, hexes.geom)
            GROUP BY hexes.geom;
        ''')

        for row in c.fetchall():
            counts.append({
                'geom': row[1],
                'count': row[0]
            })
    
    return counts

