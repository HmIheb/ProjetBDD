#packages to download using pip : geoalchemy2 / sqlalchemy / psycopg2 / pandas / geopandas 
import geopandas as gpd 
import os
from sqlalchemy import create_engine



import os
from dotenv import load_dotenv
from pathlib import Path


dotenv_path = Path(os.path.abspath('.')+"/.env")
load_dotenv(dotenv_path=dotenv_path)

DB_CONNECTION = os.getenv('DB_CONNECTION')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

engine = create_engine(f'{DB_CONNECTION}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}')
conn = engine.connect()
  

#we can modify the table later to specify the primary keys and other properties
geodf = gpd.read_file(os.path.abspath('..')+"/paris/routes.geojson")
geodf.to_postgis(name='paris_routes',con=conn,if_exists='replace')

geodf = gpd.read_file(os.path.abspath('..')+"/paris/sections.geojson")
geodf.to_postgis(name='paris_sections',con=conn,if_exists='replace')

geodf = gpd.read_file(os.path.abspath('..')+"/paris/stops.geojson")
geodf.to_postgis(name='paris_stops',con=conn,if_exists='replace')