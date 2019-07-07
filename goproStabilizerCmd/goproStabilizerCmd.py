#!/usr/bin/env python3
# encoding: utf-8
'''
goproStabilizerCmd.goproStabilizerCmd -- shortdesc

goproStabilizerCmd.goproStabilizerCmd is a description

It defines classes_and_methods

@author:     yuval herman

@copyright:  2019 yuval herman. All rights reserved.

@license:    license

@deffield    updated: Updated
'''

import sys,subprocess
from pathlib import Path
from gpmfPy.gpmfPy import gpmfStream
from pprint import pprint
import os

def twos_complement(hexstr,bits):
    value = int(hexstr,16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

def split(a, n):
    if type(n) is int:
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))
    elif type(n) is float:
        ret = []
        temp = []
        for i in range(len(a)):
            temp.append(a[i])
            if i%int(n) == 0:
                temp.append(a[i+1])
                ret.append(temp)
                temp=[]
                next(i)
            
        return(ret)
    else:
        raise ValueError("expected int or float")

def printGpmfToFile():
    with open('output.txt', 'wt') as out:
        gpmfList = gpmf.getGpmfList()
    pprint(gpmfList, stream=out)

if not len(sys.argv) > 1:
    print("you have to at leat input one video.\nUsage: goproStabilize input.mp4")

if not Path(sys.argv[1]).is_file():
    print("File not found or it does not exist")


# subprocess.run(["ffmpeg", "-y", "-i", sys.argv[1], "-codec", "copy", "-map", "0:3", "-f", "rawvideo", "out.bin"])
process = subprocess.Popen(["ffprobe", "-v", "0", "-of", "csv=p=0", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", sys.argv[1]], stdout=subprocess.PIPE)
out, err = process.communicate()
rate = out[:-1].decode("utf-8").split('/')
if len(rate)==1:
    rate = float(rate[0])
elif len(rate)==2:
    rate = float(rate[0])/float(rate[1])
else:
    raise ValueError("framerate couldn't be found.")

# os.makedirs("/tmp/goprostabilizer", exist_ok=True)
# subprocess.run(["ffmpeg", "-i", sys.argv[1], "/tmp/goprostabilizer/%d.tiff"])

with open("out.bin", "rb") as f:
    hexData = f.read()
  
gpmf = gpmfStream(hexData)
 
gyroStreams = gpmf.getStream("GYRO")
# for i in gyroStreams:
#     totalSmaples = i[0][-1][0]
#     tick = i[1][-1][0]
#     scale = i[-2][-1][0]
#     data = i[-1][-1][0]
#     print(str(totalSmaples) + " " +str(int(tick.hex(), 32)) + " " +str(scale) + " " +str(data))


for i, stream in enumerate(gyroStreams):
    num=0
    x=0
    y=0
    z=0
    print(stream[0][-1])
    samples = int(stream[0][-1][0].hex(), 16) - int(gyroStreams[i-1][0][-1][0].hex(), 16) if i > 0 else int(gyroStreams[0][0][-1][0].hex(), 16)
    print(samples/rate)
    print([len(x) for x in split(stream[2], samples/rate)])
    for data in stream[2]:
        num+=1
        z+=twos_complement(data[0:1].hex(), 16) / twos_complement(stream[1].hex(), 16)
        x+=twos_complement(data[2:3].hex(), 16) / twos_complement(stream[1].hex(), 16)
        y+=twos_complement(data[4:5].hex(), 16) / twos_complement(stream[1].hex(), 16)
    x/=num
    y/=num
    z/=num
#     print("x:" + str(x) + "\n" + "y:" + str(y) + "\n" + "z:" + str(z) + "\n")
    print()

#ffplay -i GOPR9173.mp4 -vf lenscorrection=k1=-0.5:k2=0.5

# print(int(gpmf.getStream("GYRO")[0][-1][0].hex(), 16))

print("done!")