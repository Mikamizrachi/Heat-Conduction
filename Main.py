import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QSlider, QFrame, QPushButton,
    QDoubleSpinBox, QComboBox, QHBoxLayout, QVBoxLayout, QGridLayout,
)
from PySide6.QtCharts import QChart, QChartView, QValueAxis

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

        box1 = self.make_box("red")
        box2 = self.make_box("black")

        bar = QFrame()
        bar.setFixedHeight(22)
        bar.setFixedWidth(200)  # length of the bar = distance between the boxes
        bar.setStyleSheet("background-color: #a9a9a9;")

        conductivity = self.make_spinbox(1.0, " J/s°C")
        conductivity.setFixedWidth(160)

        # label + field above the bar
        conductivity_box = QWidget()
        conductivity_box.setFixedHeight(60)
        conductivity_layout = QVBoxLayout(conductivity_box)
        conductivity_layout.setContentsMargins(0, 0, 0, 5)
        conductivity_layout.addWidget(QLabel("Conductivity"), alignment=Qt.AlignHCenter)
        conductivity_layout.addWidget(conductivity, alignment=Qt.AlignHCenter)

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
        top.addWidget(box1)
        top.addLayout(middle)
        top.addWidget(box2)
        top.addSpacing(10)
        top.addWidget(self.slider2)
        top.addStretch()

        # --- bottom part: data fields and buttons ---
        start_button = QPushButton("Start")
        start_button.setObjectName("startButton")
        start_button.setCheckable(True)

        self.temp1_label = self.make_value_label("200.0 °C")
        self.temp2_label = self.make_value_label("0.0 °C")
        
        self.slider1.valueChanged.connect(self.update_temp1)
        self.slider2.valueChanged.connect(self.update_temp2) 

        graphs_button = QPushButton("Graphs")
        graphs_button.clicked.connect(self.open_graphs)

        about_button = QPushButton("About")
        about_button.clicked.connect(self.open_about)

        rows = [
            ("Temp.", self.temp1_label, self.temp2_label, start_button),
            ("Mass", self.make_spinbox(10.0, " kg"), self.make_spinbox(10.0, " kg"), graphs_button),
            ("H. Cap.", self.make_spinbox(0.4, " J/kg°C"), self.make_spinbox(0.4, " J/kg°C"), about_button),
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
    
    def open_graphs(self):
        if self.graph_window is None:
            self.graph_window = GraphWindow()
        self.graph_window.show()

    def open_about(self):
        if self.about_window is None:
            self.about_window = AboutWindow()
        self.about_window.show()









if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))
    window = HeatTransfer()
    window.show()
    sys.exit(app.exec())
