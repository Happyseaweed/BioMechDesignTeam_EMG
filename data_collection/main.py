import serial   # pip install pyserial, not serial
import threading
import tkinter as tk
import datetime
import numpy as np
import os
import random
import time
from time import sleep

# Constants
# TODO: probably make this in a class so we can do OOP

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
    lbl.config(text=data)

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
        np.savetxt(f"saves/{datetime.datetime.now()}_Trail_0.csv", saveData, fmt="%d")
        recordedData = []
    recordingStarted = not recordingStarted

root = tk.Tk()
root.geometry("600x400")
root.title("Live Serial Data")

lbl = tk.Label(root, text="Waiting for data...", font=("Helvetica", 16))
#lbl.pack(padx=20,pady=20)
lbl.grid(row=0,column=1)

delayTime = tk.IntVar()
delayTimeEntry = tk.Entry(root, textvariable = delayTime, font=("Helvetica", 16))
rec_btn = tk.Button(root, text = 'Start' , command = toggleRecord)

delayTimeEntry.grid(row=1,column=1)
rec_btn.grid(row=2,column=1)

# =============================================================================
sleep(1)
thread = threading.Thread(target=read_serial).start()
root.mainloop()

