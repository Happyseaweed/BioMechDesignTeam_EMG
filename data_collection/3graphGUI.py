import sys
import time
import serial
import csv
import random
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from PyQt5.QtCore import QThread, pyqtSignal
import os.path


class DataGenerator(QThread):
    # 3 source data 
    new_data = pyqtSignal(int, int, int)
    
    def __init__(self, dummy_mode=True):
        super().__init__()
        self.recordingStarted = False
        self.recordedData = []
        self.dummy_mode = dummy_mode
        self._running = True

    def run(self):
        if self.dummy_mode:
            self.generate_dummy_data()
        else:
            self.read_serial_data()

    def generate_dummy_data(self):
        while self._running:
            start_time = time.time()
            while time.time() - start_time < 5 and self._running:
                v1 = random.randint(0, 100)
                v2 = random.randint(50, 150)
                v3 = random.randint(100, 200)
                self.new_data.emit(v1, v2, v3)
                if self.recordingStarted:
                    self.recordedData.append([v1, v2, v3])
                time.sleep(0.01)
            
            start_time = time.time()
            while time.time() - start_time < 2.5 and self._running:
                v1 = random.randint(1000, 2000)
                v2 = random.randint(1500, 2500)
                v3 = random.randint(2000, 3000)
                self.new_data.emit(v1, v2, v3)
                if self.recordingStarted:
                    self.recordedData.append([v1, v2, v3])
                time.sleep(0.01)

    def read_serial_data(self):
        #! PATH currently for MacOS Silicon
        #! PATH might need to be changed for Windows machines.

        ser = serial.Serial('/dev/cu.SLAB_USBtoUART', 9600, timeout=1)
        while self._running:
            if ser.in_waiting:
                line = ser.readline().decode().strip()
                try:
                    values = list(map(int, line.split(',')))
                    if len(values) == 3:
                        self.new_data.emit(*values)
                        if self.recordingStarted:
                            self.recordedData.append(values)
                except Exception as e:
                    print(f"Error: {e}")

    def stop(self):
        self._running = False
        self.wait()

class LiveGraph(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMG Data")
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Control Panel
        control_panel = QtWidgets.QWidget()
        control_layout = QtWidgets.QHBoxLayout(control_panel)
        main_layout.addWidget(control_panel)
        
        # Data Source Controls
        self.toggle_source_btn = QtWidgets.QPushButton("Switch to Serial Data")
        self.toggle_source_btn.clicked.connect(self.toggle_data_source)
        control_layout.addWidget(self.toggle_source_btn)
        
        self.source_label = QtWidgets.QLabel("Current Source: Dummy Data")
        control_layout.addWidget(self.source_label)
        
        # Recording Controls
        self.record_btn = QtWidgets.QPushButton("Start Recording (1)")
        self.record_btn.clicked.connect(self.toggle_recording)
        control_layout.addWidget(self.record_btn)
        
        self.save_btn = QtWidgets.QPushButton("Save Data (2)")
        self.save_btn.clicked.connect(self.save_data)
        control_layout.addWidget(self.save_btn)
        
        self.status_label = QtWidgets.QLabel("Not Recording")
        self.status_label.setStyleSheet("color: red; font-size: 16px;")
        control_layout.addWidget(self.status_label)
        
        self.fps_label = QtWidgets.QLabel()
        self.fps_label.setStyleSheet("color: red; font-size: 20px;")
        control_layout.addWidget(self.fps_label)
        
        # Graph Layout
        graphs_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(graphs_layout)
        
        self.plot_widgets = []
        for i, color in enumerate(['b', 'r', 'g']):
            pw = pg.PlotWidget()
            pw.setBackground('w')
            pw.setYRange(-10, 3000)
            pw.plotItem.showGrid(True, True, 0.2)
            self.plot_widgets.append(pw)
            graphs_layout.addWidget(pw)
            pw.plot(pen=pg.mkPen(color=color, width=2))

        # Real-time Graphs
        realtime_graphs = QtWidgets.QHBoxLayout()
        main_layout.addLayout(realtime_graphs)

        # History Graph
        self.history_plot = pg.PlotWidget()
        self.history_plot.setBackground('w')
        self.history_plot.setYRange(-10, 3000)
        self.history_plot.plotItem.showGrid(True, True, 0.2)
        self.history_plot.setMinimumHeight(250)
        main_layout.addWidget(self.history_plot)
        self.history_plot_segments = 0
        
        self.data = [[0]*200 for _ in range(3)]
        self.data_generator = DataGenerator(dummy_mode=True)
        self.data_generator.new_data.connect(self.update_plots)
        self.data_generator.start()
        
        self.frame_count = 0
        self.cur_time = time.time()

    def toggle_data_source(self):
        was_recording = self.data_generator.recordingStarted
        if was_recording:
            self.toggle_recording()
        
        self.data_generator.stop()
        new_mode = not self.data_generator.dummy_mode
        self.data_generator = DataGenerator(dummy_mode=new_mode)
        self.data_generator.new_data.connect(self.update_plots)
        self.data_generator.start()
        
        if was_recording:
            self.toggle_recording()
        
        source_text = "Dummy Data" if new_mode else "Serial Data"
        self.source_label.setText(f"Current Source: {source_text}")
        btn_text = "Switch to Serial Data" if new_mode else "Switch to Dummy Data"
        self.toggle_source_btn.setText(btn_text)

    def toggle_recording(self):
        self.data_generator.recordingStarted = not self.data_generator.recordingStarted
        if self.data_generator.recordingStarted:
            self.record_btn.setText("Stop Recording")
            self.status_label.setText("Recording...")
            self.status_label.setStyleSheet("color: green;")

        else:
            self.record_btn.setText("Start Recording")
            self.status_label.setText("Not Recording")
            self.status_label.setStyleSheet("color: red;")
            
            hist_data = self.data_generator.recordedData.copy()
            self.plot_history_data(hist_data)

    def save_data(self):
        if self.data_generator.recordingStarted:
            self.toggle_recording()

        # Save current recording
        save_path = './saves'
        filename = time.strftime("%Y-%m-%d_%H-%M-%S.csv")
        complete_path = os.path.join(save_path, filename)
        saved_data = self.data_generator.recordedData.copy()
        
        with open(complete_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(saved_data)
        
        # Clear temporary data
        self.history_plot_segments = 0
        self.data_generator.recordedData = []
        self.history_plot.clear()

    def update_plots(self, v1, v2, v3):
        for i, value in enumerate([v1, v2, v3]):
            self.data[i] = self.data[i][1:] + [value]
            self.plot_widgets[i].plotItem.listDataItems()[0].setData(self.data[i])
        
        self.frame_count += 1
        update_time = time.time()
        if update_time - self.cur_time >= 1.0:
            fps = self.frame_count / (update_time - self.cur_time)
            self.fps_label.setText(f"FPS: {int(fps)}")
            self.cur_time = update_time
            self.frame_count = 0

    def plot_history_data(self, data):
        if not data:
            return
        
        # Split data into channels
        x = list(range(len(data)))
        ch1 = [d[0] for d in data]
        ch2 = [d[1] for d in data]
        ch3 = [d[2] for d in data]
        
        # Plot all three channels
        self.history_plot.plot(x, ch1, pen='b')
        self.history_plot.plot(x, ch2, pen='r')
        self.history_plot.plot(x, ch3, pen='g')

        self.history_plot.addLegend()
        self.history_plot_segments+=1

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_1:
            self.toggle_recording()
        elif event.key() == QtCore.Qt.Key_2:
            self.save_data()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LiveGraph()
    window.show()
    sys.exit(app.exec_())