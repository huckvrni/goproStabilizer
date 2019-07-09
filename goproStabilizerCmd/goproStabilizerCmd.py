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
from struct import unpack

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
# subprocess.run(["ffmpeg", "-i", sys.argv[1], "/tmp/goprostabilizer/%d.tif"])
# os.makedirs("/tmp/goprostabilizer/rotate", exist_ok=True)

with open("out.bin", "rb") as f:
    hexData = f.read()

gpmf = gpmfStream(hexData)
gyroStreams = gpmf.getStream("GYRO")

j=0
GMcommands = ""
lx=0
ly=0
lz=0
x=[]
y=[]
z=[]
for i, stream in enumerate(gyroStreams):
    a=split(stream[-1][-1], rate)
    scale = unpack('>h', stream[-2][-1][0])[0]
    for cell in a:
        j+=1
        for data in cell:
            z.append(unpack('>h', data[0:2])[0])
            x.append(unpack('>h', data[2:4])[0])
            y.append(unpack('>h', data[4:6])[0])
        print(str(j) + ": " + str(sum([p>0 for p in y])) + "  " + str(sum([p<0 for p in y])) + "  " + str(len(cell)) + "  " + str(ly))
        lz += math.degrees(sum(z) / scale / 500) if len(cell) == sum([p>0 for p in z]) else 0
        lx += math.degrees(sum(x) / scale / 500) if len(cell) == sum([p>0 for p in x]) else 0
        ly += math.degrees(sum(y) / scale / 500) if len(cell) == sum([p>0 for p in y]) else 0
        lz += math.degrees(sum(z) / scale / 500) if len(cell) == sum([p<0 for p in z]) else 0
        lx += math.degrees(sum(x) / scale / 500) if len(cell) == sum([p<0 for p in x]) else 0
        ly += math.degrees(sum(y) / scale / 500) if len(cell) == sum([p<0 for p in y]) else 0
        x=[]
        y=[]
        z=[]
#             print(twos_complement(data[4:6].hex(), 16) / scale))
#         z+=math.degrees(twos_complement(cell[-1][0:2].hex(), 16) / scale)
#         x+=math.degrees(twos_complement(cell[-1][2:4].hex(), 16) / scale)
#         y+=math.degrees(twos_complement(cell[-1][4:6].hex(), 16) / scale)/100
#         print(str(i) + " " + str(y))
#         GMcommands += ("x: " + str(lx) + " y: " + str(ly) + " z: " + str(lz) + ", " + str(unpack('>f', stream[3][-1][0])[0]) + "\n")
        GMcommands += ("convert -verbose "+ str(j) + ".tif -rotate " + str(-ly) + " -gravity center -crop 50% rotate/" + str(j) +".tif\n") # -gravity center -crop 50% 
#             print("x:" + str(x) + "\n" + "y:" + str(y) + "\n" + "z:" + str(z) + "\n")
    print()

with open("/tmp/goprostabilizer/gmCommands.txt", "w") as out:
    out.write(GMcommands)
print("done!")

#ffplay -i GOPR9173.mp4 -vf lenscorrection=k1=-0.5:k2=0.5
