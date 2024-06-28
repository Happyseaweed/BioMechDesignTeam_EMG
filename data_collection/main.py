import serial
import threading
import tkinter as tk
from time import sleep

def read_serial():
    print("Test")
    with serial.Serial('/dev/cu.SLAB_USBtoUART', 115200, timeout=1) as ser:
        while ser.is_open:
            line = ser.readline() # will need to be decoded
            update_label(line.decode('utf-8'))
            sleep(0.0050)

def update_label(data):
    lbl.config(text=data)

def submit():
    dTime = delayTime.get()


root = tk.Tk()
root.geometry("600x400")
root.title("Live Serial Data")

lbl = tk.Label(root, text="Waiting for data...", font=("Helvetica", 16))
#lbl.pack(padx=20,pady=20)
lbl.grid(row=0,column=1);

delayTime = tk.IntVar()
delayTimeEntry = tk.Entry(root, textvariable = delayTime, font=("Helvetica", 16))
sub_btn = tk.Button(root, text = 'Submit',command = submit)


delayTimeEntry.grid(row=1,column=1)
sub_btn.grid(row=2,column=1)


sleep(1);
thread = threading.Thread(target=read_serial).start()




root.mainloop();
