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

df = pd.read_csv(os.path.abspath('.')+"/paris/network_combined.csv",sep=';')
df["route_I_counts"]=df["route_I_counts"].str.split(",")
df=df.explode("route_I_counts")
df['route_I_counts']=df["route_I_counts"].str.split(":").str[0]
df.rename(columns={'route_I_counts': 'route_id'}, inplace=True)
df['route_id'] = df['route_id'].astype(int)
df.to_sql(name='paris_combined',con=conn,if_exists='replace')



conn = psycopg2.connect(database=DB_DATABASE, user=DB_USERNAME, host=DB_HOST, password=DB_PASSWORD)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE paris_routes_info AS (
WITH 
table1 as (SELECT  ptd."route_I" as route_id ,count(distinct ptd.seq)+1 as nstop FROM paris_temporal_day as ptd  group by route_id),
table2 as (select route_id , avg(duration_avg) as averagetime from paris_combined group by route_id), 
table3 as (select  pr.route_name,pr."route_I" as route_id,pr.route_type from paris_routes as pr),
t1 as (select route_id, pc."from_stop_I" from paris_combined as pc),
t2 as (select route_id, pc."to_stop_I" from paris_combined as pc),
table4(route_id,depart) as (SELECT * FROM t1 except(SELECT * FROM t2)),
table5(route_id,arrival) as (SELECT * FROM t2 except(SELECT * FROM t1))


select * FROM (table3 natural join (table1 natural join table2) natural join table4) natural join table5

);



CREATE TABLE paris_staroute AS (
    with t1 as (
    SELECT distinct ptd."route_I" as route_id,max(seq) as step 
    FROM paris_temporal_day as ptd
    group by route_id
    ) 


    SELECT distinct ptd."route_I" as route_id,ptd."from_stop_I"as stop_I,max(seq) as step 
    FROM paris_temporal_day as ptd
    group by route_id,stop_I

    UNION (
        select distinct t1.route_id,ptd."to_stop_I",ptd.seq +1 as step
        from t1,paris_temporal_day as ptd
        where t1.route_id=ptd."route_I"  and ptd.seq = t1.step
    )
)
;

CREATE TABLE paris_trip AS (
    SELECT "from_stop_I", dep_time_ut,"route_I","trip_I"
    FROM paris_temporal_day
    
);
''')
#conn.commit()

#cursor.execute('''ALTER TABLE paris_trip ADD PRIMARY KEY ("from_stop_I","trip_I")''')

#cursor.execute('''ALTER TABLE paris_nodes ADD PRIMARY KEY ("stop_I");''')

#cursor.execute(''' ALTER TABLE paris_routes_info ADD PRIMARY KEY ("route_id")''')

#cursor.execute('''ALTER TABLE paris_routes_info ADD FOREIGN KEY ("arrival") REFERENCES paris_nodes("stop_I")''')

#cursor.execute('''ALTER TABLE paris_routes_info ADD FOREIGN KEY ("departure") REFERENCES paris_nodes("stop_I")''')

#cursor.execute(''' ALTER TABLE paris_staroute ADD PRIMARY KEY ("route_id","stop_I")''')

#cursor.execute('''ALTER TABLE paris_staroute ADD FOREIGN KEY ("route_id") REFERENCES paris_routes_info("route_id")''')

#cursor.execute('''ALTER TABLE paris_staroute ADD FOREIGN KEY ("stop_I") REFERENCES paris_nodes("stop_I")''')

#cursor.execute('''ALTER TABLE paris_trip ADD FOREIGN KEY ("route_I") REFERENCES paris_routes_info("route_id")''')


#conn.commit()