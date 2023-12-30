import folium, io, json, sys, math, random, os
import psycopg2
from folium.plugins import Draw, MeasureControl
from jinja2 import Template
from branca.element import Element
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from sqlalchemy import create_engine
import os
from datetime import datetime 
from dotenv import load_dotenv
from pathlib import Path



class MainWindow(QMainWindow):


    #G.U.I
    def __init__(self):
        super().__init__()

        self.resize(1000, 600)
        self.setWindowTitle("Win nro7")
	
        # main widget
        main = QWidget()
        self.setCentralWidget(main)
        main.setLayout(QHBoxLayout())
        main.setFocusPolicy(Qt.StrongFocus)

        # Table widget (for itinerary)
        self.tableWidget = QTableWidget()
        self.tableWidget.doubleClicked.connect(self.table_Click)
        self.rows = []

        # Map display
        self.webView = myWebView()
		

        #Filter part (Request criteria)
        self.controls_panel = QVBoxLayout()
        mysplit = QSplitter(Qt.Horizontal)
        mysplit.addWidget(self.tableWidget)
        mysplit.addWidget(self.webView)

        main.layout().addLayout(self.controls_panel)
        main.layout().addWidget(mysplit)

        #select city
        _label = QLabel('City :', self)
        _label.setFixedSize(40,20)
        self.city_box = QComboBox() 
        
        self.controls_panel.addWidget(_label)
        self.controls_panel.addWidget(self.city_box)
        self.city_box.addItem("paris")
        self.city_box.setCurrentIndex( 0 )
        self.city_box.currentIndexChanged.connect(self.city_change)

       

        #select starting point
        _label = QLabel('From: ', self)
        _label.setFixedSize(40,20)
        self.from_box = QComboBox() 
        self.from_box.setEditable(True)
        self.from_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.from_box.setInsertPolicy(QComboBox.NoInsert)
        self.controls_panel.addWidget(_label)
        self.controls_panel.addWidget(self.from_box)
        self.from_box.currentIndexChanged.connect(self.from_change)
        self.from_box.setFixedWidth(300)

        #select destination
        _label = QLabel('  To: ', self)
        _label.setFixedSize(30,20)
        self.to_box = QComboBox() 
        self.to_box.setEditable(True)
        self.to_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.to_box.setInsertPolicy(QComboBox.NoInsert)
        self.controls_panel.addWidget(_label)
        self.controls_panel.addWidget(self.to_box)
        self.to_box.currentIndexChanged.connect(self.to_change)
        self.to_box.setFixedWidth(300)


        #select mean of transport you want to use
        self.subway_check = QCheckBox()
        self.subway_check.setText("Subway")
        self.subway_check.setChecked(True)
        self.controls_panel.addWidget(self.subway_check)

        self.bus_check = QCheckBox()
        self.bus_check.setText("Bus")
        self.bus_check.setChecked(True)
        self.controls_panel.addWidget(self.bus_check)

        self.rail_check = QCheckBox()
        self.rail_check.setText("Rail")
        self.rail_check.setChecked(True)
        self.controls_panel.addWidget(self.rail_check)

        self.tram_check = QCheckBox()
        self.tram_check.setText("Tramway")
        self.tram_check.setChecked(True)
        self.controls_panel.addWidget(self.tram_check)


        #action button
        self.go_button = QPushButton("Go!")
        self.go_button.clicked.connect(self.button_Go)
        self.controls_panel.addWidget(self.go_button)
           
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.button_Clear)
        self.controls_panel.addWidget(self.clear_button)

        self.maptype_box = QComboBox()
        self.maptype_box.addItems(self.webView.maptypes)
        self.maptype_box.currentIndexChanged.connect(self.webView.setMap)
        self.controls_panel.addWidget(self.maptype_box)

        #point = [latitude,longitude]
        self.point1 =[0,0]
        self.point2=[0,0]
           
        self.connect_DB()

        

        self.startingpoint=True


        self.show()
    
    def city_change(self):
        self.from_box.clear()
        self.to_box.clear()

        self.from_box.addItem(str("Personalized"))
        self.to_box.addItem(str("Personalized"))

        _city = str(self.city_box.currentText())

        self.cursor.execute(""f"SELECT distinct name from {_city}_nodes """)
        self.conn.commit()
        rows = self.cursor.fetchall()

        for row in rows : 
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))
        print("Connected")

        self.from_box.setCurrentIndex(1)
        self.to_box.setCurrentIndex(1)

        #TODO set focus on the choosen city


    def from_change(self):
        if self.from_box.currentIndex()==0:
            print("personalized")
        else :
            _city = str(self.city_box.currentText())
            _from = str(self.from_box.currentText())
            self.cursor.execute(""f"SELECT lat,lon FROM {_city}_nodes WHERE name=$${_from}$$ """)
            self.conn.commit()
            rows = self.cursor.fetchall()

            self.point1=[rows[0][0],rows[0][1]]
            self.drawstartend()
        
            print("selected")
    

    def to_change(self):
        if self.from_box.currentIndex()==0:
            print("personalized")
        else :
            _city = str(self.city_box.currentText())
            _to = str(self.to_box.currentText())
            self.cursor.execute(""f"SELECT lat,lon FROM {_city}_nodes WHERE name=$${_to}$$ """)
            self.conn.commit()
            rows = self.cursor.fetchall()

            self.point2=[rows[0][0],rows[0][1]]
            self.drawstartend()
        
            print("selected")

    #Used to filter the means of transport s
    #s is the name of the table to apply the filter 
    #i is the suffixe added to route_type if there is many routes
    def tfilter(self,s,i):
        

        r=""
        if (not self.tram_check.isChecked()):
            r+=" AND "+s+".route_type"+i+"<> 0"
        
        if (not self.rail_check.isChecked()):
            r+=" AND "+s+".route_type"+i+"<> 2"
        
        if (not self.subway_check.isChecked()):
            r+=" AND "+s+".route_type"+i+"<> 1 "
        
        if (not self.bus_check.isChecked()):
            r+=" AND "+s+".route_type"+i+"<> 3"
        return r

        
    def button_Go(self):
        self.tableWidget.clearContents()

        _fromstation = str(self.from_box.currentText())
        _tostation = str(self.to_box.currentText())
        _city = str(self.city_box.currentText())

        self.rows = []

    


        #query 1 is for direct trip between two points with a sequence of : walk --> transport --> walk
        query1 = ''' 
                    WITH 
        t1 AS (
        SELECT name as name1,"stop_I",lat as lat1,lon as lon1,
        (
        6371 * acos(cos(radians('''+self.point1[0].__str__()+''')) * cos(radians(lat)) * cos(radians(lon) - radians('''+self.point1[1].__str__()+''')) +sin(radians('''+self.point1[0].__str__()+''')) * sin(radians(lat))
        )
            ) AS distance1
FROM '''+_city+'''_nodes
ORDER BY distance1
LIMIT 6),

t2 AS (
    SELECT name as name2,"stop_I",lat as lat2,lon as lon2,
    (
        6371 * acos(cos(radians('''+self.point2[0].__str__()+''')) * cos(radians(lat)) * cos(radians(lon) - radians('''+self.point2[1].__str__()+''')) +sin(radians('''+self.point2[0].__str__()+''')) * sin(radians(lat))
        )
    ) AS distance2
FROM '''+_city+'''_nodes
ORDER BY distance2
LIMIT 6),

t3 AS (
    SELECT t1.name1,lat1,lon1,t1."stop_I" as "from_stop_I",t1.distance1,ps.route_id,ps.step as step1
    FROM t1,'''+_city+'''_staroute as ps
    where t1."stop_I"=ps."stop_I" 
),

t4 AS (
    SELECT t2.name2,lat2,lon2,t2."stop_I",t2.distance2,ps.route_id,ps.step as step2
    FROM t2,'''+_city+'''_staroute as ps
    where t2."stop_I"=ps."stop_I" 
),

tf AS (
    SELECT * 
    FROM (t3 inner join t4 using(route_id))inner join '''+_city+'''_routes_info using(route_id)
    where t3.step1<t4.step2 '''+self.tfilter(_city+"_routes_info","")+'''
)

    SELECT 1 as hop,(((tf.distance1+tf.distance2)*720)+tf.averagetime*(step2-step1)) as time,tf.distance1,tf.name1,lat1,lon1,step1,route_name,route_type,name2,lat2,lon2,step2,distance2,averagetime,depart
    FROM tf
    order by time
    limit 5

'''

        query2='''
            WITH 
        t1 AS (
        SELECT name as name1,"stop_I",lat as lat1,lon as lon1,
        (
        6371 * acos(cos(radians('''+self.point1[0].__str__()+''')) * cos(radians(lat)) * cos(radians(lon) - radians('''+self.point1[1].__str__()+''')) +sin(radians('''+self.point1[0].__str__()+''')) * sin(radians(lat))
        )
            ) AS distance1
FROM '''+_city+'''_nodes
ORDER BY distance1
LIMIT 6),

t2 AS (
    SELECT name as name4,"stop_I",lat as lat4,lon as lon4,
    (
        6371 * acos(cos(radians('''+self.point2[0].__str__()+''')) * cos(radians(lat)) * cos(radians(lon) - radians('''+self.point2[1].__str__()+''')) +sin(radians('''+self.point2[0].__str__()+''')) * sin(radians(lat))
        )
    ) AS distance2
FROM '''+_city+'''_nodes
ORDER BY distance2
LIMIT 6),

t3bis AS (
    SELECT t1.name1,lat1,lon1,t1."stop_I",t1.distance1,ps.route_id as route_id1,ps.step as step1
    FROM t1,'''+_city+'''_staroute as ps
    where t1."stop_I"=ps."stop_I" 
),

t3 AS (
    SELECT distance1,name1,lat1,lon1,step1,t3bis.route_id1,pr.route_name as route_name1,pr.route_type as route_type1,pr.averagetime as avgt1,depart as depart1
    FROM t3bis inner join '''+_city+'''_routes_info as pr on t3bis.route_id1 = pr.route_id
),


t4bis AS (
    SELECT t2.name4,lat4,lon4,t2."stop_I" as stop4,t2.distance2,ps.route_id as route_id2,ps.step as step4
    FROM t2,'''+_city+'''_staroute as ps
    where t2."stop_I"=ps."stop_I" 
),

t4 AS (
    SELECT t4bis.route_id2,pr.route_name as route_name2,pr.route_type as route_type2,pr.averagetime as avgt2,t4bis.name4,t4bis.lat4,t4bis.lon4,t4bis.step4,t4bis.distance2,depart as depart2
    FROM t4bis inner join '''+_city+'''_routes_info as pr on t4bis.route_id2 = pr.route_id
),

t5bis AS (
    SELECT distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,depart1,ps."stop_I" as stop2,ps.step as step2
    FROM t3,'''+_city+'''_staroute as ps
    where t3.route_id1=ps.route_id  and t3.step1<ps.step
),

t5 AS (
    SELECT distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,depart1,pn.name as name2,pn.lat as lat2,pn.lon as lon2, stop2,step2
    from t5bis inner join '''+_city+'''_nodes as pn on t5bis.stop2=pn."stop_I"
),

t6bis AS (
    select distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,depart1,name2,lat2,lon2, stop2,step2,pw."to_stop_I" as stop3,pw.d_walk as d1
    FROM t5,'''+_city+'''_walk as pw
    where t5.stop2=pw."from_stop_I"
    UNION
    (
    select distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,depart1,name2,lat2,lon2, stop2,step2,pw."from_stop_I" as stop3,pw.d_walk as d1
    FROM t5,'''+_city+'''_walk as pw
    where t5.stop2=pw."to_stop_I"
    )
),
t6 AS (
    SELECT distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,depart1,name2,lat2,lon2, stop2,step2,d1,stop3,pn.name as name3,pn.lat as lat3,pn.lon as lon3
    from t6bis inner join '''+_city+'''_nodes as pn on t6bis.stop3=pn."stop_I"
),

t7 AS (
    select distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,depart1,name2,lat2,lon2, stop2,step2,d1,stop3,name3,lat3,lon3,ps.route_id as route_id2,ps.step as step3
    FROM t6,'''+_city+'''_staroute as ps
    where t6.stop3=ps."stop_I" and t6.route_id1<>ps.route_id
),

    tf as (
    SELECT * 
    FROM t7 inner join t4 on  t7.route_id2=t4.route_id2
    where t7.step3<t4.step4 '''+self.tfilter("t7","1")+self.tfilter("t4","2")+'''
    )

    SELECT 2 as hop, (((tf.distance1+tf.distance2+(d1/1000))*720)+tf.avgt1*(step2-step1)+ tf.avgt2*(step4-step3)) as time,distance1,name1,lat1,lon1,step1,route_name1,route_type1,name2,lat2,lon2,step2,d1,name3,lat3,lon3,step3,route_name2,route_type2,name4,lat4,lon4,step4,distance2,tf.avgt1,tf.depart1,tf.avgt2,tf.depart2
    FROM tf
    ORDER BY time
    limit 10
'''


        query3='''
            WITH 
        t1 AS (
        SELECT name as name1,"stop_I",lat as lat1,lon as lon1,
        (
        6371 * acos(cos(radians('''+self.point1[0].__str__()+''')) * cos(radians(lat)) * cos(radians(lon) - radians('''+self.point1[1].__str__()+''')) +sin(radians('''+self.point1[0].__str__()+''')) * sin(radians(lat))
        )
            ) AS distance1
FROM '''+_city+'''_nodes
ORDER BY distance1
LIMIT 6),

t2 AS (
    SELECT name as name6,"stop_I",lat as lat6,lon as lon6,
    (
        6371 * acos(cos(radians('''+self.point2[0].__str__()+''')) * cos(radians(lat)) * cos(radians(lon) - radians('''+self.point2[1].__str__()+''')) +sin(radians('''+self.point2[0].__str__()+''')) * sin(radians(lat))
        )
    ) AS distance2
FROM '''+_city+'''_nodes
ORDER BY distance2
LIMIT 6),

t3bis AS (
    SELECT t1.name1,lat1,lon1,t1."stop_I",t1.distance1,ps.route_id as route_id1,ps.step as step1
    FROM t1,'''+_city+'''_staroute as ps
    where t1."stop_I"=ps."stop_I" 
),

t3 AS (
    SELECT distance1,name1,lat1,lon1,step1,t3bis.route_id1,pr.route_name as route_name1,pr.route_type as route_type1,pr.averagetime as avgt1
    FROM t3bis inner join '''+_city+'''_routes_info as pr on t3bis.route_id1 = pr.route_id
),


t4bis AS (
    SELECT t2.name6,lat6,lon6,t2."stop_I" as stop6,t2.distance2,ps.route_id as route_id3,ps.step as step6
    FROM t2,'''+_city+'''_staroute as ps
    where t2."stop_I"=ps."stop_I" 
),

t4 AS (
    SELECT t4bis.route_id3,pr.route_name as route_name3,pr.route_type as route_type3,pr.averagetime as avgt3,t4bis.name6,t4bis.lat6,t4bis.lon6,t4bis.step6,t4bis.distance2
    FROM t4bis inner join '''+_city+'''_routes_info as pr on t4bis.route_id3 = pr.route_id
),

t5bis AS (
    SELECT distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,ps."stop_I" as stop2,ps.step as step2
    FROM t3,'''+_city+'''_staroute as ps
    where t3.route_id1=ps.route_id  and t3.step1<ps.step
),

t5 AS (
    SELECT distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,pn.name as name2,pn.lat as lat2,pn.lon as lon2, stop2,step2
    from t5bis inner join '''+_city+'''_nodes as pn on t5bis.stop2=pn."stop_I"
),

t6bis AS (
    select distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,name2,lat2,lon2, stop2,step2,pw."to_stop_I" as stop3,pw.d_walk as d1
    FROM t5,'''+_city+'''_walk as pw
    where t5.stop2=pw."from_stop_I"
    UNION
    (
    select distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,name2,lat2,lon2, stop2,step2,pw."from_stop_I" as stop3,pw.d_walk as d1
    FROM t5,'''+_city+'''_walk as pw
    where t5.stop2=pw."to_stop_I"
    )
),
t6 AS (
    SELECT distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,name2,lat2,lon2, stop2,step2,d1,stop3,pn.name as name3,pn.lat as lat3,pn.lon as lon3
    from t6bis inner join '''+_city+'''_nodes as pn on t6bis.stop3=pn."stop_I"
),

t7 AS (
    select distance1,name1,lat1,lon1,step1,route_id1,route_name1,route_type1,avgt1,name2,lat2,lon2, stop2,step2,d1,stop3,name3,lat3,lon3,ps.route_id as route_id2,ps.step as step3
    FROM t6,'''+_city+'''_staroute as ps
    where t6.stop3=ps."stop_I" and t6.route_id1<>ps.route_id
), 
t8bis AS (
    SELECT distance2,name6,lat6,lon6,step6,route_id3,route_name3,route_type3,avgt3,ps."stop_I" as stop5,ps.step as step5
    FROM t4,'''+_city+'''_staroute as ps
    where t4.route_id3=ps.route_id  and t4.step6>ps.step
),

t8 AS (
    SELECT distance2,name6,lat6,lon6,step6,route_id3,route_name3,route_type3,avgt3,pn.name as name5,pn.lat as lat5,pn.lon as lon5, stop5,step5
    from t8bis inner join '''+_city+'''_nodes as pn on t8bis.stop5=pn."stop_I"
),


t9bis AS (
    select distance2,name6,lat6,lon6,step6,route_id3,route_name3,route_type3,avgt3,name5,lat5,lon5, stop5,step5,pw."to_stop_I" as stop4,pw.d_walk as d2
    FROM t8,'''+_city+'''_walk as pw
    where t8.stop5=pw."from_stop_I"
    UNION
    (
    select distance2,name6,lat6,lon6,step6,route_id3,route_name3,route_type3,avgt3,name5,lat5,lon5, stop5,step5,pw."from_stop_I" as stop4,pw.d_walk as d2
    FROM t8,'''+_city+'''_walk as pw
    where t8.stop5=pw."to_stop_I"
    )
),
t9 AS (
    SELECT distance2,name6,lat6,lon6,step6,route_id3,route_name3,route_type3,avgt3,name5,lat5,lon5, stop5,step5,d2,stop4,pn.name as name4,pn.lat as lat4,pn.lon as lon4
    from t9bis inner join '''+_city+'''_nodes as pn on t9bis.stop4=pn."stop_I"
),
t10bis AS (
    select distance2,name6,lat6,lon6,step6,route_id3,route_name3,route_type3,avgt3,name5,lat5,lon5, stop5,step5,d2,stop4,name4, lat4,lon4,ps.route_id as route_id2,ps.step as step4
    FROM t9,'''+_city+'''_staroute as ps
    where t9.stop4=ps."stop_I" and t9.route_id3<>ps.route_id
),
t10 AS (
    SELECT distance2,name6,lat6,lon6,step6,route_id3,route_name3,route_type3,avgt3,name5,lat5,lon5, stop5,step5,d2,stop4,name4, lat4,lon4,route_id2,step4,pr.route_name as route_name2,pr.route_type as route_type2, pr.averagetime as avgt2
    FROM t10bis inner join '''+_city+'''_routes_info as pr on t10bis.route_id2 = pr.route_id
),


    tf as (
    SELECT * 
    FROM t7 inner join t10 on  t7.route_id2=t10.route_id2
    where t7.step3<t10.step4  AND route_name1<>route_name3 AND route_name2<>route_name3 AND route_name1<>route_name2'''+self.tfilter("t7","1")+self.tfilter("t10","2")+self.tfilter("t10","3")+'''
    )

    SELECT 3 as hop, (((tf.distance1+tf.distance2+((d1+d2)/1000))*720)+tf.avgt1*(step2-step1)+ tf.avgt2*(step4-step3) + tf.avgt3*(step6-step5)) as time,distance1,name1,lat1,lon1,step1,route_name1,route_type1,name2,lat2,lon2,step2,d1,name3,lat3,lon3,step3,route_name2,route_type2,name4,lat4,lon4,step4,d2,name5,lat5,lon5,step5,route_name3,route_type3,name6,lat6,lon6,step6,distance2
    FROM tf
    ORDER BY time
    limit 10
'''
        
        self.cursor.execute(query1)
        self.conn.commit()
        self.rows += self.cursor.fetchall()

        self.cursor.execute(query2)
        self.conn.commit()
        self.rows += self.cursor.fetchall()

        if len(self.rows) == 0 :
            self.cursor.execute(query3)
            self.conn.commit()
            self.rows += self.cursor.fetchall()

        #if we don't find anything we just give Walk
        if len(self.rows) == 0 : 
            self.tableWidget.setRowCount(1)
            self.tableWidget.setColumnCount(1)
            self.tableWidget.setItem(0, 0, QTableWidgetItem(str("Walk")))
            return
        

        self.tableWidget.setRowCount(len(self.rows))
        if self.rows[-1][0] == 1:
            self.tableWidget.setColumnCount(3)
        if self.rows[-1][0] == 2:
            self.tableWidget.setColumnCount(7)
        else :
            self.tableWidget.setColumnCount(11)

        i = 0
        for row in self.rows :
            #case hop 1 
            if row[0]==1:
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(row[3])))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(row[7])))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(row[9])))
            elif row[0]==2 :
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(row[3])))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(row[7])))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(row[9])))
                self.tableWidget.setItem(i, 3, QTableWidgetItem("change/walk"))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(row[14])))
                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(row[18])))
                self.tableWidget.setItem(i, 6, QTableWidgetItem(str(row[20])))
            
            elif row[0]==3 :
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(row[3])))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(row[7])))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(row[9])))
                self.tableWidget.setItem(i, 3, QTableWidgetItem("change/walk"))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(row[14])))
                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(row[18])))
                self.tableWidget.setItem(i, 6, QTableWidgetItem(str(row[20])))
                self.tableWidget.setItem(i, 7, QTableWidgetItem("change/walk"))
                self.tableWidget.setItem(i, 8, QTableWidgetItem(str(row[25])))
                self.tableWidget.setItem(i, 9, QTableWidgetItem(str(row[29])))
                self.tableWidget.setItem(i, 10, QTableWidgetItem(str(row[31])))
            
                  
            i = i + 1
            
        self.update()
            

    def button_Clear(self):
        print(self.rail_check.isChecked())
        self.webView.clearMap(self.maptype_box.currentIndex())

    def table_Click(self):
        i=self.tableWidget.currentRow()
        #case row clicked hop = 1
        if len(self.rows)==0 :

            #drawing of the way
            self.webView.addSegment(self.point1[0],self.point1[1],self.point2[0],self.point2[1])
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            dist = 6371.0 * 2 * math.atan2(math.sqrt(math.sin((math.radians(self.point2[0]) - math.radians(self.point1[0])) / 2)**2 + math.cos(math.radians(self.point1[0])) * math.cos(math.radians(self.point2[0])) * math.sin((math.radians(self.point2[1]) - math.radians(self.point1[1])) / 2)**2), math.sqrt(1 - math.sin((math.radians(self.point2[0]) - math.radians(self.point1[0])) / 2)**2 + math.cos(math.radians(self.point1[0])) * math.cos(math.radians(self.point2[0])) * math.sin((math.radians(self.point2[1]) - math.radians(self.point1[1])) / 2)**2))
            msg.setText("your trip will take "+str(round(dist))+" km approximately")
            msg.setWindowTitle("detailed itinerary")
            msg.exec()


        elif self.rows[i][0]==1:

            #description of the trip in a little window
            #now  = datetime.timestamp(datetime.now())-1481500800000
            d =datetime(2016,12,12)
            time = datetime.now().time()
            now = datetime.timestamp(datetime.combine(d,time))
            query = '''with t as (select (CASE when dep_time_ut + %d*%d-%d*720-%d > 0  then dep_time_ut + %d*%d-%d*720-%d ELSE null END) as diff,dep_time_ut 
            from paris_trip where "from_stop_I" = %d)
            select dep_time_ut from t where diff = (select min(diff) from t);
            '''%(self.rows[i][14],self.rows[i][6]-1,self.rows[i][2],now,self.rows[i][14],self.rows[i][6]-1,self.rows[i][2],now,self.rows[i][15])
            self.cursor.execute(query)
            self.conn.commit()
            rows = self.cursor.fetchall()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            if len(rows) ==0 :
                msg.setText("there is no night trip") 
            else :
                msg.setText("your trip will take "+str((round(self.rows[i][1]/60,1)))+" minutes approximately")
                walktime1 = round(int(self.rows[i][2])*720/60,1)
                walktime1_text = ('go to ' if  walktime1<0.2 else "you have to walk for about "+str(walktime1)+"to ")
                walktime2 = round(int(self.rows[i][2])*720/60,1)
                walktime2_text = ''if walktime2<0.2 else "then walk to your destination for about"+ str(walktime2)
                msg.setInformativeText(walktime1_text+self.rows[i][3]+" then take the "+self.rows[i][7]+ " at "+str(datetime.fromtimestamp(int(rows[0][0])+((int(self.rows[i][6]))-1)*int(self.rows[i][14])).time())[0:5]+" until you arrive to "+self.rows[i][9]+walktime2_text)
                msg.setWindowTitle("detailed itinerary")


            #drawing of the way
            self.webView.addSegment(self.point1[0],self.point1[1],self.rows[i][4],self.rows[i][5])
            self.webView.addSegment(self.point2[0],self.point2[1],self.rows[i][10],self.rows[i][11])
            self.webView.addSegment(self.rows[i][4],self.rows[i][5],self.rows[i][10],self.rows[i][11])

            msg.exec()
        
        elif self.rows[i][0]==3:

            #description of the trip in a little window
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("your trip will take "+str((round(self.rows[i][1]/60,1)))+" minutes approximately")
            msg.setInformativeText("you have to walk to "+self.rows[i][3]+" then take the "+self.rows[i][7]+ " until you arrive to "+self.rows[i][9]+" then walk to "+self.rows[i][14]+" then take the "+self.rows[i][18]+ " until you arrive to "+self.rows[i][20]+" then walk to "+self.rows[i][25]+" then take the "+self.rows[i][29]+ " until you arrive to "+self.rows[i][31]+" then walk to your destination")
            msg.setWindowTitle("detailed itinerary")


            #drawing of the way
            self.webView.addSegment(self.point1[0],self.point1[1],self.rows[i][4],self.rows[i][5])
            self.webView.addSegment(self.rows[i][4],self.rows[i][5],self.rows[i][10],self.rows[i][11])
            self.webView.addSegment(self.rows[i][10],self.rows[i][11],self.rows[i][15],self.rows[i][16])
            self.webView.addSegment(self.rows[i][15],self.rows[i][16],self.rows[i][21],self.rows[i][22])
            self.webView.addSegment(self.rows[i][21],self.rows[i][22],self.rows[i][26],self.rows[i][27])
            self.webView.addSegment(self.rows[i][26],self.rows[i][27],self.rows[i][32],self.rows[i][33])
            self.webView.addSegment(self.rows[i][32],self.rows[i][33],self.point2[0],self.point2[1])

            msg.exec()
        
        elif self.rows[i][0]==2:
            d =datetime(2016,12,12)
            time = datetime.now().time()
            now = datetime.timestamp(datetime.combine(d,time))
            query = '''with t as (select (CASE when dep_time_ut + %d*%d-%d*720-%d > 0  then dep_time_ut + %d*%d-%d*720-%d ELSE null END) as diff,dep_time_ut 
            from paris_trip where "from_stop_I" = %d)
            select dep_time_ut from t where diff = (select min(diff) from t);
            '''%(self.rows[i][25],self.rows[i][6]-1,self.rows[i][2],now,self.rows[i][25],self.rows[i][6]-1,self.rows[i][2],now,self.rows[i][26])
            self.cursor.execute(query)
            self.conn.commit()
            rows = self.cursor.fetchall()
            print(rows)
            now = rows[0][0]+(self.rows[i][13])/1000*720+(self.rows[i][12]-self.rows[i][6])*self.rows[i][25]
            query = '''with t as (select (CASE when dep_time_ut + %d*%d-%d*720-%d > 0  then dep_time_ut + %d*%d-%d*720-%d ELSE null END) as diff,dep_time_ut 
            from paris_trip where "from_stop_I" = %d)
            select dep_time_ut from t where diff = (select min(diff) from t);
            '''%(self.rows[i][27],self.rows[i][23]-1,self.rows[i][24],now,self.rows[i][27],self.rows[i][23]-1,self.rows[i][24],now,self.rows[i][28])
            
            self.cursor.execute(query)
            self.conn.commit()
            rows = self.cursor.fetchall()
            print(rows)
            #description of the trip in a little window
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("your trip will take "+str((round(self.rows[i][1]/60,1)))+" minutes approximately")
            msg.setInformativeText("you have to walk to "+self.rows[i][3]+" then take the "+self.rows[i][7]+ " until you arrive to "+self.rows[i][9]+" then walk to "+self.rows[i][14]+" then take the "+self.rows[i][18]+ " until you arrive to "+self.rows[i][20]+" then walk to your destination")
            msg.setWindowTitle("detailed itinerary")


            #drawing of the way
            self.webView.addSegment(self.point1[0],self.point1[1],self.rows[i][4],self.rows[i][5])
            self.webView.addSegment(self.rows[i][4],self.rows[i][5],self.rows[i][10],self.rows[i][11])
            self.webView.addSegment(self.rows[i][10],self.rows[i][11],self.rows[i][15],self.rows[i][16])
            self.webView.addSegment(self.rows[i][15],self.rows[i][16],self.rows[i][21],self.rows[i][22])
            self.webView.addSegment(self.point2[0],self.point2[1],self.rows[i][21],self.rows[i][22])

            msg.exec()
        



    def connect_DB(self):
        dotenv_path = Path(os.path.abspath('.')+"/.env")
        load_dotenv(dotenv_path=dotenv_path)

        DB_CONNECTION = os.getenv('DB_CONNECTION')
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')
        DB_DATABASE = os.getenv('DB_DATABASE')
        DB_USERNAME = os.getenv('DB_USERNAME')
        DB_PASSWORD = os.getenv('DB_PASSWORD')

        
        
        self.conn = psycopg2.connect(database=DB_DATABASE, user=DB_USERNAME, host=DB_HOST, password=DB_PASSWORD)
        self.cursor = self.conn.cursor()

        _city = str(self.city_box.currentText())
        self.from_box.addItem(str("Personalized"))
        self.to_box.addItem(str("Personalized"))

        self.cursor.execute(""f"SELECT distinct name from {_city}_nodes """)
        self.conn.commit()
        rows = self.cursor.fetchall()

        for row in rows : 
            self.from_box.addItem(str(row[0]))
            self.to_box.addItem(str(row[0]))
        print("Connected")

        self.from_box.setCurrentIndex(1)
        self.to_box.setCurrentIndex(1)

    def mouseClick(self, lat, lng):

        
        print(f"Clicked on: latitude {lat}, longitude {lng}")
        
        if self.startingpoint :
            self.from_box.setCurrentIndex(0)
            self.point1=[lat,lng]
        else :
            self.to_box.setCurrentIndex(0)
            self.point2=[lat,lng]
        self.startingpoint = not self.startingpoint

        self.drawstartend()

    def drawstartend(self):
        self.webView.addPointMarker(self.point1[0], self.point1[1])
        self.webView.addPointMarker(self.point2[0], self.point2[1])
        print(self.point1[0])



class myWebView (QWebEngineView):
    def __init__(self):
        super().__init__()

        self.maptypes = ["OpenStreetMap", "Stamen Terrain", "stamentoner", "cartodbpositron"]
        self.setMap(0)


    def add_customjs(self, map_object):
        my_js = f"""{map_object.get_name()}.on("click",
                 function (e) {{
                    var data = `{{"coordinates": ${{JSON.stringify(e.latlng)}}}}`;
                    console.log(data)}}); """
        e = Element(my_js)
        html = map_object.get_root()
        html.script.get_root().render()
        html.script._children[e.get_name()] = e

        return map_object


    def handleClick(self, msg):
        data = json.loads(msg)
        lat = data['coordinates']['lat']
        lng = data['coordinates']['lng']


        window.mouseClick(lat, lng)


    def addSegment(self, lat1, lng1, lat2, lng2):
        js = Template(
        """
        L.polyline(
            [ [{{latitude1}}, {{longitude1}}], [{{latitude2}}, {{longitude2}}] ], {
                "color": "red",
                "opacity": 1.0,
                "weight": 4,
                "line_cap": "butt"
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude1=lat1, longitude1=lng1, latitude2=lat2, longitude2=lng2 )

        self.page().runJavaScript(js)


    def addMarker(self, lat, lng):
        js = Template(
        """
        L.marker([{{latitude}}, {{longitude}}] ).addTo({{map}});
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": "#3388ff",
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#3388ff",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def addPointMarker(self, lat, lng):
        js = Template(
        """
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": 'green',
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": 'green',
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def setMap (self, i):
        self.mymap = folium.Map(location=[48.8619, 2.3519], tiles=self.maptypes[i], zoom_start=12, prefer_canvas=True)

        self.mymap = self.add_customjs(self.mymap)

        page = WebEnginePage(self)
        self.setPage(page)

        data = io.BytesIO()
        self.mymap.save(data, close_file=False)

        self.setHtml(data.getvalue().decode())

    def clearMap(self, index):
        self.setMap(index)



class WebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        #print(msg)
        if 'coordinates' in msg:
            self.parent.handleClick(msg)


       
			
if __name__ == '__main__':
    sys.argv.append('--no-sandbox')
    app = QApplication(sys.argv) 
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())