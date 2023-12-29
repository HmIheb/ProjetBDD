import pandas as pd
import psycopg2
import os.path
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
  

cities = ['paris']


for city in cities:

   #city_walk
   df = pd.read_csv(os.path.abspath('.')+"/"+city+"/network_walk.csv",sep=';')
   df.to_sql(name=city+'_walk',con=conn,if_exists='replace',index=False)
   
   #city_bus
   df = pd.read_csv(os.path.abspath('.')+"/"+city+"/network_bus.csv",sep=';')
   df.to_sql(name=city+'_bus',con=conn,if_exists='replace',index=False)
   

   #city_rail
   df = pd.read_csv(os.path.abspath('.')+"/"+city+"/network_rail.csv",sep=';')
   df.to_sql(name=city+'_rail',con=conn,if_exists='replace',index=False)
   
   #city_subway
   df = pd.read_csv(os.path.abspath('.')+"/"+city+"/network_subway.csv",sep=';')
   df.to_sql(name=city+'_subway',con=conn,if_exists='replace',index=False)
  
   #city_nodes
   df = pd.read_csv(os.path.abspath('.')+"/"+city+"/network_nodes.csv",sep=';')
   df.to_sql(name=city+'_nodes',con=conn,if_exists='replace',index=False)
   
   #"+city+"_combined
   df = pd.read_csv(os.path.abspath('.')+"/"+city+"/network_combined.csv",sep=';')
   df.to_sql(name=city+'_combined',con=conn,if_exists='replace',index=False)
  

   #city_temporal_day
   df = pd.read_csv(os.path.abspath('.')+"/"+city+"/network_temporal_day.csv",sep=';')
   df.to_sql(name=city+'_temporal_day',con=conn,if_exists='replace',index=False)

   #city_temporal_week
   reader = pd.read_csv(os.path.abspath('.')+"/"+city+"/network_temporal_week.csv",sep=';',chunksize=1000000)
   #size = 0
   for rows in reader : 
      df = pd.DataFrame(rows)
      df.to_sql(name=city+'_temporal_week',con=conn,if_exists='append',index=False)
      #size +=df.shape[0]

   #city_tram
   df = pd.read_csv(os.path.abspath('.')+"/"+city+"/network_tram.csv",sep=';')
   df.to_sql(name=city+'_tram',con=conn,if_exists='replace',index=False)
   