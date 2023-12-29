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

#paris_walk
df = pd.read_csv(os.path.abspath('..')+"/paris/network_walk.csv",sep=';')
df.to_sql(name='paris_walk',con=conn,if_exists='replace',index=False)
# cursor.execute("""SELECT count(*) from paris_walk""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"walk : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_bus
df = pd.read_csv(os.path.abspath('..')+"/paris/network_bus.csv",sep=';')
df.to_sql(name='paris_bus',con=conn,if_exists='replace',index=False)
# cursor.execute("""SELECT count(*) from paris_bus""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"bus : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_rail
df = pd.read_csv(os.path.abspath('..')+"/paris/network_rail.csv",sep=';')
df.to_sql(name='paris_rail',con=conn,if_exists='replace',index=False)
# cursor.execute("""SELECT count(*) from paris_rail""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"rail : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_subway
df = pd.read_csv(os.path.abspath('..')+"/paris/network_subway.csv",sep=';')
df.to_sql(name='paris_subway',con=conn,if_exists='replace',index=False)
# cursor.execute("""SELECT count(*) from paris_subway""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"subway : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_nodes
df = pd.read_csv(os.path.abspath('..')+"/paris/network_nodes.csv",sep=';')
df.to_sql(name='paris_nodes',con=conn,if_exists='replace',index=False)
# cursor.execute("""SELECT count(*) from paris_nodes""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"nodes : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_combined
df = pd.read_csv(os.path.abspath('..')+"/paris/network_combined.csv",sep=';')
df.to_sql(name='paris_combined',con=conn,if_exists='replace',index=False)
# cursor.execute("""SELECT count(*) from paris_combined""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"combined : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_temporal_day
df = pd.read_csv(os.path.abspath('..')+"/paris/network_temporal_day.csv",sep=';')
df.to_sql(name='paris_temporal_day',con=conn,if_exists='replace',index=False)
# cursor.execute("""SELECT count(*) from paris_temporal_day""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"temporal_day : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")


#paris_temporal_week
reader = pd.read_csv(os.path.abspath('..')+"/paris/network_temporal_week.csv",sep=';',chunksize=1000000)
#size = 0
for rows in reader : 
   df = pd.DataFrame(rows)
   df.to_sql(name='paris_temporal_week',con=conn,if_exists='append',index=False)
   #size +=df.shape[0]
#print(size)   
# cursor.execute("""SELECT count(*) from paris_temporal_week""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"temporal_week : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_tram

df = pd.read_csv(os.path.abspath('..')+"/paris/network_tram.csv",sep=';')
df.to_sql(name='paris_tram',con=conn,if_exists='replace',index=False)
# cursor.execute("""SELECT count(*) from paris_tram""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"tram : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")
