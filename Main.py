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

        # --- top part: slider | body | conductor | body | slider ---
        slider1 = self.make_slider(200)
        slider2 = self.make_slider(0)

        box1 = self.make_box("red")
        box2 = self.make_box("black")

        bar = QFrame()
        bar.setFixedHeight(22)
        bar.setStyleSheet("background-color: #a9a9a9;")

        conductivity = self.make_spinbox(1.0, " J/s°C")
        conductivity.setFixedWidth(110)

        middle = QVBoxLayout()
        middle.addStretch()
        middle.addWidget(QLabel("Conductivity"), alignment=Qt.AlignHCenter)
        middle.addWidget(conductivity, alignment=Qt.AlignHCenter)
        middle.addWidget(bar)
        middle.addStretch()

        top = QHBoxLayout()
        top.addWidget(slider1)
        top.addWidget(box1)
        top.addLayout(middle, stretch=1)
        top.addWidget(box2)
        top.addWidget(slider2)

        # --- bottom part: data fields and buttons ---
        start_button = QPushButton("Start")
        start_button.setObjectName("startButton")
        start_button.setCheckable(True)  # toggle button

        graphs_button = QPushButton("Graphs")
        graphs_button.clicked.connect(self.open_graphs)

        about_button = QPushButton("About")
        about_button.clicked.connect(self.open_about)

        rows = [
            ("Temp.", self.make_value_label("200.0 °C"), self.make_value_label("0.0 °C"), start_button),
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

        self.resize(600, 400)

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
        label.setObjectName("valueLabel")  # read-only, styled in style.css
        return label

    def open_graphs(self):
        if self.graph_window is None:
            self.graph_window = GraphWindow()
        self.graph_window.show()

    def open_about(self):
        if self.about_window is None:
            self.about_window = AboutWindow()
        self.about_window.show()


class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Graph Window")

        # empty chart with axes only
        chart = QChart()
        chart.legend().hide()
        axis_x = QValueAxis()
        axis_x.setTitleText("Time (s)")
        axis_x.setRange(0, 1)
        axis_y = QValueAxis()
        axis_y.setTitleText("Temperature (°C)")
        axis_y.setRange(0, 1)
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)

        chart_view = QChartView(chart)
        chart_view.setMinimumSize(420, 320)

        body_choice = QComboBox()
        body_choice.addItems(["Body 1", "Body 2"])

        controls = QVBoxLayout()
        controls.addWidget(body_choice)
        controls.addWidget(QPushButton("Draw"))
        controls.addWidget(QPushButton("Clear"))
        controls.addWidget(QPushButton("Export to CSV"))
        controls.addStretch()

        layout = QHBoxLayout(self)
        layout.addWidget(chart_view, stretch=1)
        layout.addLayout(controls)

        self.resize(650, 420)


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("About")

        picture = QLabel()
        picture.setPixmap(self.make_picture())
        picture.setAlignment(Qt.AlignCenter)

        title = QLabel("<h2>Heat Transfer</h2>")
        title.setAlignment(Qt.AlignCenter)

        text = QLabel(
            "Simulation of heat conduction between two bodies "
            "connected by a conductor.<br><br>Written by Mika Mizrachi"
        )
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignCenter)

        link = QLabel(f'<a href="{GITHUB_URL}">Project on GitHub</a>')
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(picture)
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addWidget(link)

        self.setFixedWidth(380)

    def make_picture(self):
        """Small drawing: hot body - conductor - cold body."""
        pixmap = QPixmap(220, 80)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.fillRect(80, 32, 60, 16, QColor("#a9a9a9"))
        painter.fillRect(20, 5, 60, 70, QColor("red"))
        painter.fillRect(140, 5, 60, 70, QColor("black"))
        painter.end()
        return pixmap


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))
    window = HeatTransfer()
    window.show()
    sys.exit(app.exec())
