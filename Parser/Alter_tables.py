import psycopg2 

conn = psycopg2.connect(database="transport", user="transport", host="localhost", password="transport")
cursor = conn.cursor()

cursor.execute('''ALTER TABLE paris_nodes ADD PRIMARY KEY ("stop_I");''')

cursor.execute('''ALTER TABLE paris_walk ADD PRIMARY KEY ("from_stop_I","to_stop_I")''')

cursor.execute('''ALTER TABLE paris_bus ADD PRIMARY KEY ("from_stop_I","to_stop_I");''')


cursor.execute('''ALTER TABLE paris_tram ADD PRIMARY KEY ("from_stop_I","to_stop_I")''')

cursor.execute('''ALTER TABLE paris_rail ADD PRIMARY KEY ("from_stop_I","to_stop_I")''')

cursor.execute('''ALTER TABLE paris_subway ADD PRIMARY KEY ("from_stop_I","to_stop_I")''')

cursor.execute('''ALTER TABLE paris_combined ADD PRIMARY KEY ("from_stop_I","to_stop_I",route_type)''')

cursor.execute('''ALTER TABLE paris_temporal_day ADD PRIMARY KEY ("from_stop_I","to_stop_I","trip_I")''')


#cursor.execute('''ALTER TABLE paris_temporal_week ADD PRIMARY KEY ("from_stop_I","to_stop_I","trip_I")''')
cursor.execute('''ALTER TABLE paris_stops ADD PRIMARY KEY ("stop_I")''')

cursor.execute('''ALTER TABLE paris_sections ADD PRIMARY KEY ("from_stop_I","to_stop_I","route_type")''')

cursor.execute('''ALTER TABLE paris_routes ADD PRIMARY KEY ("route_I")''')

cursor.execute('''ALTER TABLE paris_temporal_day ADD FOREIGN KEY ("route_I") REFERENCES paris_routes("route_I")''')
# route_I exists in paris_temporal_I but not paris_routes
#cursor.execute('''ALTER TABLE paris_temporal_week ADD FOREIGN KEY ("route_I") REFERENCES paris_routes("route_I")''')

conn.commit()