import sys
import random
import time
from PyQt5 import QtWidgets
import pyqtgraph as pg
from PyQt5.QtCore import QThread, pyqtSignal

class DataGenerator(QThread):
    new_data = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.recordingStarted = False
        self.recordedData = []
    
    def run(self):
        # Send fake data with random pockets of EMG
        while True:
            start_time = time.time()
            while time.time() - start_time < 5:
                decoded = random.randint(0, 100)
                time.sleep(0.01)
                self.new_data.emit(decoded)
                if self.recordingStarted:
                    self.recordedData.append(decoded)
            
            start_time = time.time()
            while time.time() - start_time < 2.5:
                decoded = random.randint(1000, 2000)
                time.sleep(0.01)
                self.new_data.emit(decoded)
                if self.recordingStarted:
                    self.recordedData.append(decoded)

class LiveGraph(QtWidgets.QMainWindow):
    def __init__(self):
        #raw data (writes to file)
        self.rawdata = []

        super().__init__()
        self.setWindowTitle("EMG Data")
        self.setGeometry(100, 100, 800, 500)
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        self.graphWidget.setYRange(-10, 2400)
        self.data_line = self.graphWidget.plot(pen=pg.mkPen(color='b', width=2))
        
        self.data = [0] * 200
        self.fps_label = QtWidgets.QLabel(self)
        self.fps_label.setStyleSheet("QLabel { color : red; font-size: 20px; }")
        self.fps_label.setGeometry(720, 10, 100, 20)
        self.frame_count = 0
        self.cur_time = time.time()

        #EMG data generator (ty wallace :3)
        self.data_generator = DataGenerator()
        self.data_generator.new_data.connect(self.update_label)
        self.data_generator.start()
    
    def update_label(self, decoded):
        """
        >Remove oldest data, add new to stack, and update plot
        >Updates framerate display
        """
        self.data = self.data[1:] + [decoded]
        self.data_line.setData(self.data)
        
        self.frame_count += 1
        update_time = time.time()    
        if update_time - self.cur_time >= 1.0:
            fps = self.frame_count / (update_time - self.cur_time)
            self.fps_label.setText(f"FPS: {int(fps)}")
            self.cur_time = update_time
            self.frame_count = 0

    def store(self, decoded):
        self.rawdata.append(decoded)

    def write(self):
        """write to file"""
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    liveGraph = LiveGraph()
    liveGraph.show()
    sys.exit(app.exec_())
