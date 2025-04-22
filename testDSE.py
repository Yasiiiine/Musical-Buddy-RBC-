from Modules.tuner.TunerObject import NoteFinder
import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt

CHUNK = 1024*4
FORMAT = pyaudio.paInt16
RATE = 44100
CHANNELS = 1

p = pyaudio.PyAudio()
audioStream = p.open(rate = RATE,channels= CHANNELS, format=FORMAT, input = True,output=True,frames_per_buffer=CHUNK)



figu, axes = plt.subplots(1,figsize=(15,7))
x = np.arange(0,2*CHUNK,2)
line, = axes.plot(x, np.random.rand(CHUNK), '-', lw=2)

axes.set_xlim(0,2*CHUNK)
axes.set_ylim(0,255)
plt.setp(axes, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])

# show the plot
plt.show(block=False)

while True:
        data = audioStream.read(CHUNK)
        dataint = struct.unpack(str(2*CHUNK) + 'B', data)
        datatest = np.array(dataint,dtype='uint8')[::2] + 128
        line.set_ydata(datatest)
        figu.canvas.draw()
        figu.canvas.flush_events()
        



        

