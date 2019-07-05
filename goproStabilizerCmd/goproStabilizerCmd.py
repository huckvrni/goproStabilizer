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
for i in gpmf.getStream("GYRO")[0][-1]:
    [print(twos_complement(i[x:x+2].hex(), 16)) for x in range(0, 3)]
    print()
# print(int(gpmf.getStream("GYRO")[0][-1][0].hex(), 16))
# with open('output.txt', 'wt') as out:
#     gpmfList = gpmf.getGpmfList()
#     pprint(gpmfList, stream=out)

print("done!")