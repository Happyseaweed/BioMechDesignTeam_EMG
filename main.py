import serial   # pip install pyserial, not serial
import threading
import tkinter as tk
import datetime
import numpy as np
import os
import random
import time
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import matplotlib.colors as mccolor

# Constants
# TODO: probably make this in a class so we can do OOP
print("Hello World")
recordingStarted = False
recordedData = []

def read_serial():
    print("Test")
    global recordingStarted
    global recordedData
    try:
        with serial.Serial('/dev/cu.SLAB_USBtoUART', 9600, timeout=2) as ser:
            while ser.is_open:
                line = ser.readline() # will need to be decoded
                decoded = line.decode('utf-8')
                update_label(decoded)
                # sleep(0.0050)
                if recordingStarted:
                    decoded = decoded[:-2]
                    recordedData.append(decoded) 
    # When you don't have esp32 connected but just work on the GUI itself
    except Exception as e:
        print("Currently at offline mode, generating random data")
        # Send fake data with random pockets of EMG
        while True:
            start_time = time.time()
            while time.time()-start_time < 5:
                decoded = random.randint(0, 100)
                time.sleep(0.01)
                update_label(decoded)
                if recordingStarted:
                    recordedData.append(decoded)
            start_time = time.time()
            while time.time()-start_time < 2.5:
                decoded = random.randint(1000, 2000)
                time.sleep(0.01)
                update_label(decoded)
                if recordingStarted:
                    recordedData.append(decoded)


def update_label(data):
    root.after(0, lbl.config, {'text': data})

def toggleRecord():
    global recordingStarted
    global recordedData
    if (not recordingStarted): 
        rec_btn.config(text="Stop")
        print("RECORDING [STARTED]\n")
    else: 
        rec_btn.config(text="Start")
        print("RECORDING [STOPPED]\n")
        saveData = np.array(recordedData, dtype=np.int16)
        print(saveData)
        print(saveData.shape)
        if not os.path.exists("saves/"):
            os.makedirs("saves")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        np.savetxt(f"saves/{timestamp}_Trail_0.csv", saveData, fmt="%d")
        recordedData = []
    recordingStarted = not recordingStarted

root = tk.Tk()
root.geometry("600x800")
root.title("Live Serial Data")

fig, ax = plt.subplots()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=3, column=0, columnspan=3, pady=20)

def update_plot(data):
    ax.clear()
    ax.plot(data, color='blue', label = 'Data Values')
    recent_data = data[-100:]
    avg = np.mean(recent_data)
    ax.scatter(len(data)-1, avg, color='red', label='Point Average')
    ax.annotate(f'{avg:.2f}', xy=(len(data)-1, avg), xytext=(len(data)-1, avg+0.5),
                arrowprops=dict(facecolor='red', shrink=0.005),
                bbox=dict(boxstyle="round,pad=0.3", edgecolor='red', facecolor='white'))
    ax.legend(loc='upper right')
    canvas.draw()

def animate(i):
    if recordedData:
        update_plot(recordedData)

def close():
    print("closing")
    root.quit()
    root.destroy()


ani = animation.FuncAnimation(fig, animate, interval=1000)

lbl = tk.Label(root, text="Waiting for data...", font=("Helvetica", 16))
lbl.grid(row=0, column=0, columnspan=3, pady=20)

delayTime = tk.IntVar()
delayTimeEntry = tk.Entry(root, textvariable = delayTime, font=("Helvetica", 16))
delayTimeEntry.grid(row=1, column=1, padx=20, pady=10)

rec_btn = tk.Button(root, text = 'Start' , command = toggleRecord)
rec_btn.grid(row=2, column=1, padx=20, pady=10)

delayTimeEntry.grid(row=1,column=1)
rec_btn.grid(row=2,column=1)

close_btn = tk.Button(root, text = 'Close Program', command = close)
close_btn.grid(row=10, column=1, padx=50, pady=10)

# Make sure everything is centered in the window
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# =============================================================================
sleep(1)
thread = threading.Thread(target=read_serial).start()
root.mainloop()
