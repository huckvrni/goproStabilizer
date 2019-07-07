'''
Created on 3 Jul 2019

@author: herman
'''
from enum import Enum

class GPMF_TYPE(Enum):
	GPMF_TYPE_STRING_ASCII = 'c' #single byte 'c' style character string
	GPMF_TYPE_SIGNED_BYTE = 'b'#single byte signed number
	GPMF_TYPE_UNSIGNED_BYTE = 'B' #single byte unsigned number
	GPMF_TYPE_SIGNED_SHORT = 's'#16-bit integer
	GPMF_TYPE_UNSIGNED_SHORT = 'S'#16-bit integer
	GPMF_TYPE_FLOAT = 'f' #32-bit single precision float (IEEE 754)
	GPMF_TYPE_FOURCC = 'F' #32-bit four character tag 
	GPMF_TYPE_SIGNED_LONG = 'l'#32-bit integer
	GPMF_TYPE_UNSIGNED_LONG = 'L' #32-bit integer
	GPMF_TYPE_Q15_16_FIXED_POINT = 'q' # Q number Q15.16 - 16-bit signed integer (A) with 16-bit fixed point (B) for A.B value (range -32768.0 to 32767.99998). 
	GPMF_TYPE_Q31_32_FIXED_POINT = 'Q' # Q number Q31.32 - 32-bit signed integer (A) with 32-bit fixed point (B) for A.B value. 
	GPMF_TYPE_SIGNED_64BIT_INT = 'j' #64 bit signed long
	GPMF_TYPE_UNSIGNED_64BIT_INT = 'J' #64 bit unsigned long	
	GPMF_TYPE_DOUBLE = 'd' #64 bit double precision float (IEEE 754)
	GPMF_TYPE_UTC_DATE_TIME = 'U' #128-bit ASCII Date + UTC Time format yymmddhhmmss.sss - 16 bytes ASCII (years 20xx covered)
	GPMF_TYPE_GUID = 'G' #128-bit ID (like UUID)

	GPMF_TYPE_COMPLEX = '?' #for sample with complex data structures, base size in bytes.  Data is either opaque, or the stream has a TYPE structure field for the sample.

	GPMF_TYPE_NEST = 0 # used to nest more GPMF formatted metadata 

class gpmfStream(object):
	'''
	classdocs
	'''
	bytesArray = []
	gpmfList = []
	index = 0

	def __init__(self, bytesArray):
		'''
		Constructor
		'''
		self.bytesArray = bytesArray
		self.gpmfList = self.__gpmfToList()

	def getGpmfList(self):
		if len(self.gpmfList) > 0:
			return self.gpmfList
		else:
			self.gpmfList = self.__gpmfToList()
		return self.gpmfList
	
	def getGpmfAt(self, i, end=0):
		if i+8 > len(self.bytesArray):
			raise IndexError("gpmf index out of range")
		if end != 0:
			gpmfKLV = []
			while i < end:
				key, ltype, lsize, lrepeat = self.resolveKlv(i)
				i+=8
				padds = 0
				if lsize*lrepeat%4!=0:
					padds = 4-(lsize*lrepeat%4)
# 				if self.bytesArray[i+(lsize*lrepeat)] == 0: #chr(ltype) == GPMF_TYPE.GPMF_TYPE_STRING_ASCII.value and lsize == 1:
# 					padds = 2
				if ltype == GPMF_TYPE.GPMF_TYPE_NEST.value:
					currend=lsize*lrepeat+padds+i
					data = self.getGpmfAt(i, currend)
# 					break
				else:
					data = [self.bytesArray[i:i+(lsize*lrepeat)][k:k+lsize] for k in range(0, len(self.bytesArray[i:i+(lsize*lrepeat)]), lsize)]
				gpmfKLV.append([key, chr(ltype), lsize*lrepeat, data])
				i+=lsize*lrepeat+padds
			self.index = i
			return(gpmfKLV)
		
		key, ltype, lsize, lrepeat = self.resolveKlv(i)
		i+=8
		padds = 0
		if ltype == GPMF_TYPE.GPMF_TYPE_NEST.value:
			currend=lsize*lrepeat+padds+i
			end=lsize*lrepeat+padds+i
			gpmfKLV = [key, chr(ltype), lsize*lrepeat, self.getGpmfAt(i, currend)]
		else:
			gpmfKLV = [key, chr(ltype), lsize*lrepeat, self.bytesArray[i:i+(lsize*lrepeat)]]
		if end == 0:
			self.index = i
			return(gpmfKLV)
		else:
			i += lsize*lrepeat+padds
		self.index = i
		return(gpmfKLV)
	
	def resolveKlv(self, i):
		key = str(self.bytesArray[i:i+4]) #chr(self.bytesArray[i])+chr(self.bytesArray[i+1])+chr(self.bytesArray[i+2])+chr(self.bytesArray[i+3])
		i+=4
		ltype = self.bytesArray[i]
		lsize = self.bytesArray[i+1]
		lrepeat = int(self.bytesArray[i+2:i+3].hex() + self.bytesArray[i+3:i+4].hex(), 16)
		return([key, ltype, lsize, lrepeat])
	
	def __gpmfToList(self):
		gpmfList = []
		while self.index < len(self.bytesArray):
			gpmfList.append(self.getGpmfAt(self.index))
		return gpmfList

	def getStream(self, key):
		keyList = []
		for x in self.gpmfList:
			for stream in x[-1]:
				if str(bytes(key, "ASCII")) == stream[-1][-1][0]:
					keyList.append(stream[-1])
		return(keyList)