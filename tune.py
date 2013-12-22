#!/usr/bin/env python
# coding=utf-8
# [original source](https://blog.blahgeek.com/yong-pythonba-zhou-jie-lun-bian-wei-zhou-jie-lun.html)
# Increase frequency of songs
# modified by C19<classone2010@gmail.com>

import pylab
import numpy
import wave
import sys

import pdb

def getChannelsData(file):
    wav = wave.open(file,'rb')
    datatype = numpy.dtype('<i' + str(wav.getsampwidth()))  # Little endian
    raw_data = numpy.fromstring(wav.readframes(wav.getnframes()), datatype)
    channels_data = [raw_data[i::wav.getnchannels()] for i in xrange(wav.getnchannels())]
    chunksize = wav.getframerate() / 8
    wav_params = wav.getparams()
    return channels_data, chunksize, datatype, wav_params

def tune(data, multible):
    fft_data = numpy.fft.rfft(data)
    #round(i/multible)=>shrink wave[increase frequncy]
    #/1.5849 => reduce amplitude to wipe out noise
    new_fft = [fft_data[round(i/multible)]/1.5849 for i in xrange(len(fft_data))]
    transformed = numpy.fft.irfft(new_fft)
    drawWave([data, transformed])#, data, transformed])
    return transformed

def tuneChannel(data, multible, chunksize):
    ret = []
    for i in xrange(0, len(data), chunksize):
        chunk = data[i:i+chunksize]
        ret += list(tune(chunk, multible))
    return ret

def tuneSong(file, multible):
    channels_data, chunksize, datatype, wav_params = getChannelsData(file)
    channels_data = [tuneChannel(channel, multible, chunksize) for channel in channels_data]
    final_data = []
    for j in xrange(len(channels_data[0])):
        for i in xrange(len(channels_data)):
            final_data += [channels_data[i][j]]
    final_data = numpy.array(final_data, dtype=datatype).tostring()
    return final_data, wav_params

def writeNewSong(tuned, outfile, wav_params):
    new_wav = wave.open(outfile, 'w')
    new_wav.setparams(wav_params)
    new_wav.writeframes(tuned)
    new_wav.close()

def drawWave(wave_data):
    i = 0
    #f, axarr = pylab.subplots(len(wave_data), sharex=True)
    #axarr[0].xlabel("time (seconds)")
    def _drawWave(wave):
        #pylab.subplot(i) 
        #axarr[i].plot(wave)
        pylab.plot(wave)
    for wave in wave_data:
        _drawWave(wave)
        #i += 1   #uncomment this to draw in sperate picture
    pylab.show()

if __name__ == '__main__':
    print("python tune.py original.wav 1.25 new.wav\n  1.25 is the rate to increase the frequency.\n")
    if(len(sys.argv)<2): exit()
    tuned, wav_params = tuneSong(sys.argv[1], sys.argv[2] if len(sys.argv)>3 else 1.25)
    writeNewSong(tuned, (sys.argv[3] if len(sys.argv)>4 else 'out.wav'), wav_params)