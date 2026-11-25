import sys
import csv
import os
from pathlib import Path

from PySide6.QtCore import Qt , QTimer
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QSlider, QFrame, QPushButton,
    QDoubleSpinBox, QComboBox, QHBoxLayout, QVBoxLayout, QGridLayout,QMessageBox
)
from PySide6.QtCharts import QChart, QChartView, QValueAxis , QLineSeries
from About import About
from Body import Body

STYLE_FILE = Path(__file__).with_name("style.css")
MATERIALS = { "Custom": None, "Wood": 1700, "Aluminum": 897, "Glass": 840, "Iron": 449, "Copper": 385,}
GITHUB_URL = "https://github.com/Mikamizrachi/Heat-Conduction"


class HeatTransfer(QWidget):
    def __init__(self):
        super().__init__()
        self.about_window = None
        self.graph_window = None
        self.body1 = None
        self.body2 = None
        self.time = 0
        self.time_history = []
        self.body1_temp_history = []
        self.body2_temp_history = []


        self.dt = 0.05
        self.timer = QTimer()
        self.timer.setInterval(int(self.dt*1000))
        self.timer.timeout.connect(self.timer_method)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Heat Transfer")

       
        self.slider1 = self.make_slider(200)
        self.slider2 = self.make_slider(0)

        self.box1 = self.make_box("red")
        self.box2 = self.make_box("black")

        bar = QFrame()
        bar.setFixedHeight(22)
        bar.setFixedWidth(200) 
        bar.setStyleSheet("background-color: #a9a9a9;")

        self.conductivity = self.make_spinbox(1.0, " J/s°C")
        self.conductivity.setFixedWidth(160)

        conductivity_box = QWidget()
        conductivity_box.setFixedHeight(60)
        conductivity_layout = QVBoxLayout(conductivity_box)
        conductivity_layout.setContentsMargins(0, 0, 0, 5)
        conductivity_layout.addWidget(QLabel("Conductivity"), alignment=Qt.AlignHCenter)
        conductivity_layout.addWidget(self.conductivity, alignment=Qt.AlignHCenter)

        
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
        top.setSpacing(0)  
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
        self.start_button.toggled.connect(self.start_stop_button_method)

        self.temp1_label = self.make_value_label("200.0 °C")
        self.temp2_label = self.make_value_label("0.0 °C")
        
        self.slider1.valueChanged.connect(self.left_temperature_changed)
        self.slider2.valueChanged.connect(self.right_temperature_changed)

        graphs_button = QPushButton("Graphs")
        graphs_button.clicked.connect(self.open_graphs)

        about_button = QPushButton("About")
        about_button.clicked.connect(self.open_about)

        self.mass1 = self.make_spinbox(10.0, " kg")
        self.mass2 = self.make_spinbox(10.0, " kg")
        self.cap1 = self.make_spinbox(0.4, " J/kg°C")
        self.cap2 = self.make_spinbox(0.4, " J/kg°C")
        
        self.material1 = self.make_material_choice()
        self.material2 = self.make_material_choice()
        self.material1.currentTextChanged.connect(self.material1_changed)
        self.material2.currentTextChanged.connect(self.material2_changed)

        self.heater1 = self.make_spinbox(0, " W", 0, 1000)
        self.heater2 = self.make_spinbox(0, " W", 0, 1000)

        rows = [
            ("Temp.", self.temp1_label, self.temp2_label, self.start_button),
            ("Mass", self.mass1, self.mass2, graphs_button),
            ("Material", self.material1, self.material2, None),
            ("H. Cap.", self.cap1, self.cap2, about_button),
            ("Heater", self.heater1, self.heater2, None),]

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        for row, (name, left, right, button) in enumerate(rows):
            grid.addWidget(QLabel(name), row, 0)
            grid.addWidget(left, row, 1)
            if button is not None:
                grid.addWidget(button, row, 2, alignment=Qt.AlignHCenter)
            grid.addWidget(right, row, 3)
            grid.addWidget(QLabel(name), row, 4, alignment=Qt.AlignRight)
        grid.setColumnStretch(2, 1)

        self.room_temp = self.make_spinbox(20, " °C", 0, 200)
        self.heat_loss = self.make_spinbox(0, " J/s°C", 0, 100)  

        settings = QHBoxLayout()
        settings.addWidget(QLabel("Room temp."))
        settings.addWidget(self.room_temp)
        settings.addStretch()
        settings.addWidget(QLabel("Heat loss"))
        settings.addWidget(self.heat_loss)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_layout.addLayout(top)
        main_layout.addLayout(grid)
        main_layout.addLayout(settings)

        self.resize(600, 480)

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

    def make_spinbox(self, value, suffix, minimum=0.01, maximum=10000):
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setValue(value)
        spin.setSuffix(suffix)
        return spin

    def make_value_label(self, text):
        label = QLabel(text)
        label.setObjectName("valueLabel")  
        return label

    
    def make_material_choice(self):
        choice = QComboBox()
        choice.addItems(list(MATERIALS.keys()))
        return choice

    def material1_changed(self, name):
        self.apply_material(name, self.cap1)

    def material2_changed(self, name):
        self.apply_material(name, self.cap2)

    def apply_material(self, name, cap_spin):
        value = MATERIALS[name]
        if value is None:
            cap_spin.setEnabled(True)
        else:
            cap_spin.setValue(value)
            cap_spin.setEnabled(False)
    
    def left_temperature_changed(self, value):
        self.show_temperature(self.box1, self.temp1_label, value)

    def right_temperature_changed(self, value):
        self.show_temperature(self.box2, self.temp2_label, value)

    def show_temperature(self, box, label, temp):
        label.setText(f"{temp:.1f} °C")
      
        red = int(temp / 200 * 255)
        red = max(0, min(255, red))  
        box.setStyleSheet(f"background-color: rgb({red}, 0, 0);")

    def start_stop_button_method(self, checked):
        if checked:
            self.body1 = Body(self.mass1.value(), self.cap1.value(), self.slider1.value())
            self.body2 = Body(self.mass2.value(), self.cap2.value(), self.slider2.value())
            self.time = 0
            self.time_history = []
            self.body1_temp_history = []
            self.body2_temp_history = []
            self.save_history() 
            self.start_button.setText("Stop")
            self.timer.start()
        else:

            self.timer.stop()
            self.start_button.setText("Start")

        for widget in [self.slider1, self.slider2, self.mass1, self.mass2,
                       self.material1, self.material2, self.conductivity]:
            widget.setEnabled(not checked)

        self.cap1.setEnabled(not checked and self.material1.currentText() == "Custom")
        self.cap2.setEnabled(not checked and self.material2.currentText() == "Custom")

    def timer_method(self):
        dt = self.dt

        cap1 = self.body1.mass * self.body1.specific_heat
        cap2 = self.body2.mass * self.body2.specific_heat

        t1 = self.body1.temp
        t2 = self.body2.temp
        q = self.conductivity.value() * (t1 - t2) * dt
        t_final = (cap1 * t1 + cap2 * t2) / (cap1 + cap2)
        q_max = cap1 * (t1 - t_final)
        if abs(q) > abs(q_max):
            q = q_max
        self.body1.add_heat(-q)  
        self.body2.add_heat(q)  
        heat1 = self.heater1.value() * dt - self.room_loss(self.body1.temp, cap1, dt)
        heat2 = self.heater2.value() * dt - self.room_loss(self.body2.temp, cap2, dt)
        t1 = self.body1.add_heat(heat1)
        t2 = self.body2.add_heat(heat2)

        self.slider1.setValue(round(t1))
        self.slider2.setValue(round(t2))
        self.show_temperature(self.box1, self.temp1_label, t1)
        self.show_temperature(self.box2, self.temp2_label, t2)

        self.time = self.time + dt
        self.save_history()

        if abs(t1 - t2) < 0.1:
            self.start_button.setChecked(False)  
            QMessageBox.information(self, "Equilibrium",f"The temperatures are equal ({t1:.1f} °C) after {self.time:.1f} s.")

     
    def room_loss(self, temp, cap, dt):
        room = self.room_temp.value()
        loss = self.heat_loss.value() * (temp - room) * dt
        max_loss = cap * (temp - room)
        if abs(loss) > abs(max_loss):
            loss = max_loss
        return loss       

    def save_history(self):
        self.time_history.append(round(self.time, 2))
        self.body1_temp_history.append(self.body1.temp)
        self.body2_temp_history.append(self.body2.temp)

    
    def open_graphs(self):
        if self.graph_window is None:
            self.graph_window = GraphWindow(self)
        self.graph_window.show()

    def open_about(self):
        if self.about_window is None:
            self.about_window = About()
        self.about_window.show()

    def closeEvent(self, event):
        self.timer.stop()
        if self.graph_window is not None:
            self.graph_window.close()
        if self.about_window is not None:
            self.about_window.close()


class GraphWindow(QWidget):

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Graph Window")
        self.setGeometry(560, 100, 430, 290)

    
        self.chart = QChart()
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
        self.body_choice.setGeometry(310, 60, 110, 28)

        self.draw_button = QPushButton("Draw", self)
        self.draw_button.setGeometry(310, 100, 110, 30)
        self.draw_button.clicked.connect(self.draw_clicked)

        self.clear_button = QPushButton("Clear", self)
        self.clear_button.setGeometry(310, 140, 110, 30)
        self.clear_button.clicked.connect(self.clear_clicked)

        self.export_button = QPushButton("Export to CSV", self)
        self.export_button.setGeometry(310, 180, 110, 30)
        self.export_button.clicked.connect(self.export_clicked)


    def draw_clicked(self):
        times = self.main_window.time_history
        if len(times) == 0:
            return  
        if self.body_choice.currentText() == "Body 1":
            temps = self.main_window.body1_temp_history
            color = "red"
        else:
            temps = self.main_window.body2_temp_history
            color = "blue"

        series = QLineSeries()
        series.setName(self.body_choice.currentText())  
        pen = QPen(QColor(color))
        pen.setWidth(2)
        series.setPen(pen)
        for i in range(len(times)):
            series.append(times[i], temps[i])


        self.chart.addSeries(series)
        series.attachAxis(self.axis_x)
        series.attachAxis(self.axis_y)


        self.axis_x.setRange(0, times[-1])
        self.axis_y.setRange(0, 200)


    def clear_clicked(self):
        self.chart.removeAllSeries()

  
    def export_clicked(self):
        times = self.main_window.time_history
        temps1 = self.main_window.body1_temp_history
        temps2 = self.main_window.body2_temp_history
        if len(times) == 0:
            return  

        file_path = Path(__file__).with_name("results.csv")

        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Time (s)", "Temperature 1 (°C)", "Temperature 2 (°C)"])
            for i in range(len(times)):
                writer.writerow([times[i], temps1[i], temps2[i]])

        os.startfile(file_path)      




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))
    window = HeatTransfer()
    window.show()
    sys.exit(app.exec())
