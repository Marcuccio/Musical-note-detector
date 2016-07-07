import sys
import random
import math
import os     
import pyaudio
from scipy import signal
from random import * 
import numpy as np
from scipy.signal import blackmanharris, fftconvolve
from numpy import argmax, sqrt, mean, diff, log
from matplotlib.mlab import find
import time

def build_default_tuner_range():
    
    return {65.41:'Do2', 
            69.30:'Do2#',
            73.42:'Re2',  
            77.78:'Mi2b', 
            82.41:'Mi2',  
            87.31:'Fa2',  
            92.50:'Fa2#',
            98.00:'Sol2', 
            103.80:'Sol2#',
            110.00:'La2', 
            116.50:'Si2b',
            123.50:'Si2', 
            130.80:'Do3', 
            138.60:'Do3#',
            146.80:'Re3',  
            155.60:'Mi3b', 
            164.80:'Mi3',  
            174.60:'Fa3',  
            185.00:'Fa3#',
            196.00:'Sol3',
            207.70:'Sol3#',
            220.00:'La3',
            233.10:'Si3b',
            246.90:'Si3', 
            261.60:'Do4', 
            277.20:'Do4#',
            293.70:'Re4', 
            311.10:'Mi4b', 
            329.60:'Mi4', 
            349.20:'Fa4', 
            370.00:'Fa4#',
            392.00:'Sol4',
            415.30:'Sol4#',
            440.00:'La4',
            466.20:'Si4b',
            493.90:'Si4', 
            523.30:'Do5', 
            554.40:'Do5#',
            587.30:'Re5', 
            622.30:'Mi5b', 
            659.30:'Mi5', 
            698.50:'Fa5', 
            740.00:'Fa5#',
            784.00:'Sol5',
            830.60:'Sol5#',
            880.00:'La5',
            932.30:'Si5b',
            987.80:'Si5', 
            1047.00:'Do6',
            1109.0:'Do6#',
            1175.0:'Re6', 
            1245.0:'Mi6b', 
            1319.0:'Mi6', 
            1397.0:'Fa6', 
            1480.0:'Fa6#',
            1568.0:'Sol6',
            1661.0:'Sol6#',
            1760.0:'La6',
            1865.0:'Si6b',
            1976.0:'Si6', 
            2093.0:'Do7'
            } 

RATE=48000
BUFFERSIZE=3072
FORMAT = pyaudio.paInt16
soundgate = 19
tunerNotes = build_default_tuner_range()
frequencies = np.array(sorted( tunerNotes.keys()) )

def callback(in_data, frame_count, time_info, status):
    raw_data_signal = np.fromstring( in_data,dtype= np.int16 )
    signal_level = round(abs(loudness(raw_data_signal)),2)               #### find the volume from the audio
    try: 
        inputnote = round(freq_from_autocorr(raw_data_signal,RATE),2)    #### find the freq from the audio
    except:
        inputnote = 0

    if inputnote > frequencies[len(tunerNotes)-1]:
        return ( raw_data_signal, pyaudio.paContinue )
    if inputnote < frequencies[0]:
        return ( raw_data_signal, pyaudio.paContinue )
    if signal_level > soundgate:
        return ( raw_data_signal, pyaudio.paContinue )
    targetnote = closest_value_index(frequencies, round(inputnote, 2))
    print tunerNotes[frequencies[targetnote]]
    return ( in_data, pyaudio.paContinue )

# See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
def freq_from_autocorr(raw_data_signal, fs):                          
    corr = fftconvolve(raw_data_signal, raw_data_signal[::-1], mode='full')
    corr = corr[len(corr)/2:]
    d = diff(corr)
    start = find(d > 0)[0]
    peak = argmax(corr[start:]) + start
    px, py = parabolic(corr, peak)
    return fs / px
    
# See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
def parabolic(f, x): 
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)

    return (xv, yv)

def loudness(chunk):
    data = np.array(chunk, dtype=float) / 32768.0
    ms = math.sqrt(np.sum(data ** 2.0) / len(data))
    if ms < 10e-8: ms = 10e-8

    return 10.0 * math.log(ms, 10.0)
        
def find_nearest(array, value):
    index = (np.abs(array - value)).argmin()
    return array[index]

def closest_value_index(array, guessValue):
    # Find closest element in the array, value wise
    closestValue = find_nearest(array, guessValue)
    # Find indices of closestValue
    indexArray = np.where(array == closestValue)
    # Numpys 'where' returns a 2D array with the element index as the value

    return indexArray[0][0]

def main():
	p = pyaudio.PyAudio()
	stream = p.open( format = FORMAT,
			channels=1,
			rate = RATE, 
			input=True,
			output=False,
			frames_per_buffer = BUFFERSIZE,
			stream_callback = callback )

	stream.start_stream()

	while stream.is_active():
	    time.sleep( 0.1 )

	stream.stop_stream()
	stream.close()

if __name__ == "__main__":
	main()