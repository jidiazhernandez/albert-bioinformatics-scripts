#!/usr/bin/env python

'''



Copyright 2010 Wu Albert Cheng <albertwcheng@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''

from albertcommon import *
from sys import *
from random import *

##shuffle per row

def printUsageAndExit(programName):
	print >> stderr,programName,"infile cols"
	exit()
	
	
if __name__=='__main__':
	
	programName=argv[0]
	args=argv[1:]
	
	try:
		filename,cols=args
	except:
		printUsageAndExit(programName)
		
	
	startRow=1
	headerRow=1
	fs="\t"
	#startRow=headerRow+1
	#headerRow-=1
	header,prestarts=getHeader(filename,headerRow,startRow,fs)
		
	cols=getCol0ListFromCol1ListStringAdv(header,cols)
	colI=range(0,len(cols)) #shuffle this
	
	lino=0
	fil=open(filename)
	for lin in fil:
		lino+=1
		fields=lin.strip("\r\n").split(fs)
		if lino>=startRow:
			colTmp=getSubvector(fields,cols) #store tmp unshuffled list for target cols
			shuffle(colI)
			#now shuffle cols according to colI
			for i in range(0,len(cols)):
				fields[cols[i]]=colTmp[colI[i]]
		
		print >> stdout,fs.join(fields)
			
			
	fil.close()
	