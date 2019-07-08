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
import math

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
        cell = []
        num=0
        adder=int(n/(len(a)%n)+.5)
        cellSize=int(len(a)/n+.5)
        for i in range(len(a)):
            if num == adder and len(cell)>=cellSize:
                num=0
                cell.append(a[i])
            
            if len(cell)>=cellSize:
                ret.append(cell)
                cell=[]
                num+=1
            cell.append(a[i])
        return(ret)
    else:
        raise ValueError("expected int or float")

def printGpmfToFile():
    with open('output.txt', 'wt') as out:
        gpmfList = gpmf.getGpmfList()
    pprint(gpmfList, stream=out)

if not len(sys.argv) > 1:
    print("you have to at least input one video.\nUsage: goproStabilize input.mp4")
    sys.exit(1)

if not Path(sys.argv[1]).is_file():
    print("File not found or it does not exist")
    sys.exit(1)


subprocess.run(["ffmpeg", "-y", "-i", sys.argv[1], "-codec", "copy", "-map", "0:3", "-f", "rawvideo", "out.bin"])
process = subprocess.Popen(["ffprobe", "-v", "0", "-of", "csv=p=0", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", sys.argv[1]], stdout=subprocess.PIPE)
out, err = process.communicate()
rate = out[:-1].decode("utf-8").split('/')
if len(rate)==1:
    rate = float(rate[0])
elif len(rate)==2:
    rate = float(rate[0])/float(rate[1])
else:
    raise ValueError("framerate couldn't be found.")

os.makedirs("/tmp/goprostabilizer", exist_ok=True)
subprocess.run(["ffmpeg", "-i", sys.argv[1], "/tmp/goprostabilizer/%d.tif"])
os.makedirs("/tmp/goprostabilizer/rotate", exist_ok=True)

with open("out.bin", "rb") as f:
    hexData = f.read()

gpmf = gpmfStream(hexData)
gyroStreams = gpmf.getStream("GYRO")

j=0
GMcommands = ""
for i, stream in enumerate(gyroStreams):
    x=0
    y=0
    z=0
    a=split(stream[-1][-1], rate)
    scale = int(stream[-2][-1][0].hex(), 16)
    for cell in a:
        j+=1
        for data in cell:
            z+=math.radians(twos_complement(data[0:2].hex(), 16) / scale)
            x+=math.radians(twos_complement(data[2:4].hex(), 16) / scale)
            y+=math.radians(twos_complement(data[4:6].hex(), 16) / scale)
#             print(j)
        GMcommands += ("convert -verbose "+ str(j) + ".tif -rotate " + str(-y*11) + " -gravity center -crop 50% rotate/" + str(j) +".tif\n")
#             print("x:" + str(x) + "\n" + "y:" + str(y) + "\n" + "z:" + str(z) + "\n")
    print()

with open("/tmp/goprostabilizer/gmCommands.txt", "w") as out:
    out.write(GMcommands)
print("done!")

#ffplay -i GOPR9173.mp4 -vf lenscorrection=k1=-0.5:k2=0.5
