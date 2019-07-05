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

def twos_complement(hexstr,bits):
    value = int(hexstr,16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

if not len(sys.argv) > 1:
    print("you have to at leat input one video.\nUsage: goproStabilize input.mp4")

if not Path(sys.argv[1]).is_file():
    print("File not found or it does not exist")


# subprocess.run(["ffmpeg", "-y", "-i", sys.argv[1], "-codec", "copy", "-map", "0:3", "-f", "rawvideo", "out.bin"])
# 
with open("out.bin", "rb") as f:
    hexData = f.read()
 
gpmf = gpmfStream(hexData)
print(int(gpmf.getStream("GYRO")[0][0].hex() ,16))
for x in range(1, len(gpmf.getStream("GYRO"))-2):
    print(int(gpmf.getStream("GYRO")[x][0].hex() ,16) - int(gpmf.getStream("GYRO")[x-1][0].hex() ,16))


#ffplay -i GOPR9173.mp4 -vf lenscorrection=k1=-0.5:k2=0.5

# print(int(gpmf.getStream("GYRO")[0][-1][0].hex(), 16))
# with open('output.txt', 'wt') as out:
#     gpmfList = gpmf.getGpmfList()
#     pprint(gpmfList, stream=out)

print("done!")