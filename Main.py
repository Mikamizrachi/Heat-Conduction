import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QSlider, QFrame, QPushButton,
    QDoubleSpinBox, QComboBox, QHBoxLayout, QVBoxLayout, QGridLayout,
)
from PySide6.QtCharts import QChart, QChartView, QValueAxis
from About import About

STYLE_FILE = Path(__file__).with_name("style.css")
GITHUB_URL = "https://github.com/Mikamizrachi/Heat-Conduction"


class HeatTransfer(QWidget):
    def __init__(self):
        super().__init__()
        # add other window
        self.about_window = None
        self.graph_window = None
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Heat Transfer")

       
        self.slider1 = self.make_slider(200)
        self.slider2 = self.make_slider(0)

        self.box1 = self.make_box("red")
        self.box2 = self.make_box("black")

        bar = QFrame()
        bar.setFixedHeight(22)
        bar.setFixedWidth(200)  # length of the bar = distance between the boxes
        bar.setStyleSheet("background-color: #a9a9a9;")

        self.conductivity = self.make_spinbox(1.0, " J/s°C")
        self.conductivity.setFixedWidth(160)

        # label + field above the bar
        conductivity_box = QWidget()
        conductivity_box.setFixedHeight(60)
        conductivity_layout = QVBoxLayout(conductivity_box)
        conductivity_layout.setContentsMargins(0, 0, 0, 5)
        conductivity_layout.addWidget(QLabel("Conductivity"), alignment=Qt.AlignHCenter)
        conductivity_layout.addWidget(self.conductivity, alignment=Qt.AlignHCenter)

        # empty space below the bar, same height as above -> bar stays in the middle
        spacer = QWidget()
        spacer.setFixedHeight(60)

        middle = QVBoxLayout()
        middle.setSpacing(0)
        middle.addStretch()
        middle.addWidget(conductivity_box)
        middle.addWidget(bar)
        middle.addWidget(spacer)
        middle.addStretch()

        top = QHBoxLayout()
        top.setSpacing(0)  # the bar touches the boxes
        top.addStretch()
        top.addWidget(self.slider1)
        top.addSpacing(10)
        top.addWidget(self.box1)
        top.addLayout(middle)
        top.addWidget(self.box2)
        top.addSpacing(10)
        top.addWidget(self.slider2)
        top.addStretch()

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        self.start_button.setCheckable(True)  
        self.start_button.toggled.connect(self.start_toggled)

        self.temp1_label = self.make_value_label("200.0 °C")
        self.temp2_label = self.make_value_label("0.0 °C")
        
        self.slider1.valueChanged.connect(self.update_temp1)
        self.slider2.valueChanged.connect(self.update_temp2) 

        graphs_button = QPushButton("Graphs")
        graphs_button.clicked.connect(self.open_graphs)

        about_button = QPushButton("About")
        about_button.clicked.connect(self.open_about)

        self.mass1 = self.make_spinbox(10.0, " kg")
        self.mass2 = self.make_spinbox(10.0, " kg")
        self.cap1 = self.make_spinbox(0.4, " J/kg°C")
        self.cap2 = self.make_spinbox(0.4, " J/kg°C")

        rows = [
            ("Temp.", self.temp1_label, self.temp2_label, self.start_button),
            ("Mass", self.mass1, self.mass2, graphs_button),
            ("H. Cap.", self.cap1, self.cap2, about_button),
        ]

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        for row, (name, left, right, button) in enumerate(rows):
            grid.addWidget(QLabel(name), row, 0)
            grid.addWidget(left, row, 1)
            grid.addWidget(button, row, 2, alignment=Qt.AlignHCenter)
            grid.addWidget(right, row, 3)
            grid.addWidget(QLabel(name), row, 4, alignment=Qt.AlignRight)
        grid.setColumnStretch(2, 1)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_layout.addLayout(top)
        main_layout.addLayout(grid)

        self.resize(560, 400)

    def make_slider(self, value):
        slider = QSlider(Qt.Vertical)
        slider.setRange(0, 200)
        slider.setValue(value)
        slider.setFixedHeight(180)
        return slider

    def make_box(self, color):
        box = QFrame()
        box.setFixedSize(90, 140)
        box.setStyleSheet(f"background-color: {color};")
        return box

    def make_spinbox(self, value, suffix):
        spin = QDoubleSpinBox()
        spin.setRange(0.01, 10000)
        spin.setValue(value)
        spin.setSuffix(suffix)
        return spin

    def make_value_label(self, text):
        label = QLabel(text)
        label.setObjectName("valueLabel")  
        return label
    
    def update_temp1(self, value):
        self.temp1_label.setText(f"{value:.1f} °C")

    def update_temp2(self, value):
        self.temp2_label.setText(f"{value:.1f} °C")

    def start_toggled(self, checked):
        if checked:
            self.start_button.setText("Stop")
        else:
            self.start_button.setText("Start")
    
    def open_graphs(self):
        if self.graph_window is None:
            self.graph_window = GraphWindow(self)
        self.graph_window.show()

    def open_about(self):
        if self.about_window is None:
            self.about_window = About()
        self.about_window.show()


class GraphWindow(QWidget):

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Graph Window")
        self.setGeometry(560, 100, 430, 290)

    
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.setBackgroundVisible(False)           
        self.chart.setPlotAreaBackgroundBrush(Qt.white)  
        self.chart.setPlotAreaBackgroundVisible(True)

        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Time (s)")
        self.axis_x.setRange(0, 1)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Temperature (°C)")
        self.axis_y.setRange(0, 1)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)

        self.chart_view = QChartView(self.chart, self)
        self.chart_view.setGeometry(10, 10, 290, 270)

        self.body_choice = QComboBox(self)
        self.body_choice.addItems(["Body 1", "Body 2"])
        self.body_choice.setGeometry(310, 20, 110, 28)

        self.draw_button = QPushButton("Draw", self)
        self.draw_button.setGeometry(310, 60, 110, 30)

        self.clear_button = QPushButton("Clear", self)
        self.clear_button.setGeometry(310, 100, 110, 30)

        self.export_button = QPushButton("Export to CSV", self)
        self.export_button.setGeometry(310, 140, 110, 30)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))
    window = HeatTransfer()
    window.show()
    sys.exit(app.exec())
