#packages to download using pip : geoalchemy2 / sqlalchemy / psycopg2 / pandas / geopandas 
import geopandas as gpd 
from sqlalchemy import create_engine

engine = create_engine("postgresql://transport:transport@localhost/transport")
conn = engine.connect()

#we can modify the table later to specify the primary keys and other properties
geodf = gpd.read_file("paris/routes.geojson")
geodf.to_postgis(name='paris_routes',con=conn,if_exists='replace')

geodf = gpd.read_file("paris/sections.geojson")
geodf.to_postgis(name='paris_sections',con=conn,if_exists='replace')

geodf = gpd.read_file("paris/stops.geojson")
geodf.to_postgis(name='paris_stops',con=conn,if_exists='replace')