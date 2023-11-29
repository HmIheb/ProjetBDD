import pandas as pd
import psycopg2
from sqlalchemy import create_engine

engine = create_engine("postgresql://l3info_42:L3INFO_42@10.11.11.22/l3info_42")
conn = engine.connect()

conn2 = psycopg2.connect(database="l3info_42", user="l3info_42", host="10.11.11.22", password="L3INFO_42")
cursor = conn2.cursor()

  
#paris_walk
df = pd.read_csv("network_walk.csv",sep=';')
df.to_sql(name='paris_walk',con=conn,if_exists='replace')
# cursor.execute("""SELECT count(*) from paris_walk""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"walk : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_bus
df = pd.read_csv("network_bus.csv",sep=';')
df.to_sql(name='paris_bus',con=conn,if_exists='replace')
# cursor.execute("""SELECT count(*) from paris_bus""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"bus : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_rail
df = pd.read_csv("network_rail.csv",sep=';')
df.to_sql(name='paris_rail',con=conn,if_exists='replace')
# cursor.execute("""SELECT count(*) from paris_rail""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"rail : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_subway
df = pd.read_csv("network_subway.csv",sep=';')
df.to_sql(name='paris_subway',con=conn,if_exists='replace')
# cursor.execute("""SELECT count(*) from paris_subway""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"subway : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_nodes
df = pd.read_csv("network_nodes.csv",sep=';')
df.to_sql(name='paris_nodes',con=conn,if_exists='replace')
# cursor.execute("""SELECT count(*) from paris_nodes""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"nodes : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_combined
df = pd.read_csv("network_combined.csv",sep=';')
df.to_sql(name='paris_combined',con=conn,if_exists='replace')
# cursor.execute("""SELECT count(*) from paris_combined""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"combined : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_temporal_day
df = pd.read_csv("network_temporal_day.csv",sep=';')
df.to_sql(name='paris_temporal_day',con=conn,if_exists='replace')
# cursor.execute("""SELECT count(*) from paris_temporal_day""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"temporal_day : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_temporal_week
df = pd.read_csv("network_temporal_week.csv",sep=';')
df.to_sql(name='paris_temporal_week',con=conn,if_exists='replace')
# cursor.execute("""SELECT count(*) from paris_temporal_week""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"temporal_week : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")

#paris_tram
df = pd.read_csv("network_tram.csv",sep=';')
df.to_sql(name='paris_tram',con=conn,if_exists='replace')
# cursor.execute("""SELECT count(*) from paris_tram""")
# conn2.commit()
# rows = cursor.fetchall()
# print(f"tram : existed in data_frame {df.shape[0]} inserted {rows[0][0]}")
