import folium, io, json, sys, math, random, os
#import psycopg2
from folium.plugins import Draw, MeasureControl
from jinja2 import Template
from branca.element import Element
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



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
        self.city_box.setCurrentIndex( 2 )
        self.controls_panel.addWidget(_label)
        self.controls_panel.addWidget(self.city_box)

        #select starting point
        _label = QLabel('From: ', self)
        _label.setFixedSize(40,20)
        self.from_box = QComboBox() 
        self.from_box.setEditable(True)
        self.from_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.from_box.setInsertPolicy(QComboBox.NoInsert)
        self.controls_panel.addWidget(_label)
        self.controls_panel.addWidget(self.from_box)

        #select destination
        _label = QLabel('  To: ', self)
        _label.setFixedSize(30,20)
        self.to_box = QComboBox() 
        self.to_box.setEditable(True)
        self.to_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.to_box.setInsertPolicy(QComboBox.NoInsert)
        self.controls_panel.addWidget(_label)
        self.controls_panel.addWidget(self.to_box)


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
           
        self.connect_DB()

        self.startingpoint = True
                   
        self.show()

    def button_Go(self):
        print(self.subway_check.isChecked())

    def button_Clear(self):
        print(self.rail_check.isChecked())

    def table_Click(self):
        print("Display")

    def connect_DB(self):
        #self.conn = psycopg2.connect(database="l3info_12", user="l3info_12", host="10.11.11.22", password="L3INFO_12")
        #self.cursor = self.conn.cursor()
        print("Connected")




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