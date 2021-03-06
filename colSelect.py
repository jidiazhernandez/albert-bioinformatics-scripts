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

from sys import stderr,stdout,argv, exit
from albertcommon import *
from getopt import getopt
from colStat import *

def usageExit(programName):
	print >> stderr, "Usage:",programName,"filename colSelector"
	print >> stderr, "Options:"
	print >> stderr, "-F,-t,-d,--fs string input separator string"
	print >> stderr, "-o,--ofs string   output separator string"
	print >> stderr, "-s,--sort sort the coordinate. Default no sorting"
	print >> stderr, "-r,--headerRow row set the header row"
	print >> stderr, "-f,--format format: [col1] col0 name excel"
	print >> stderr, "-c,--condense. Condense 1,2,3,4 => 1-4"
	print >> stderr, "-n,--not. Complement the selection. e.g., for a file with 10 columns: colSelect.py --not filename 2-3,6-9 selects 1,4-5,10. Using this option force the column selections to be sorted" 
	explainColumns(stderr)	
	exit()

def condenseNumbers(numbers):
	blockStart=None
	blockEnd=None
	
	condensed=[]
	
	for num in numbers:
		if blockStart==None:
			blockStart=num
			blockEnd=num
		else:
			if num!=blockEnd+1:
				#end this
				condensed.append((blockStart,blockEnd))
				blockStart=num
				blockEnd=num
			else:
				blockEnd=num
				
	#output last
	condensed.append((blockStart,blockEnd))
	return condensed

if __name__=="__main__":
	programName=argv[0]
	optlist,args=getopt(argv[1:],'t:F:d:r:s:o:cn',['ofs=','fs=','headerRow=','format=','sort','condense','not'])

	sort=False
	headerRow=1
	ofs=" "
	fs="\t"
	format="col1"
	formats=["col0","col1","excel","name"]
	condense=False
	condense_sep="-"
	complement=False
	
	if len(args)!=2:
		usageExit(programName)
	else:
		fileName,colString=args
	
		for a,v in optlist:
			if a in ["-F","-t","-d","--fs"]:
				fs=replaceSpecialChar(v)
			elif a in ["-o","--ofs"]:
				ofs=replaceSpecialChar(v)
			elif a in ["-r","--headerRow"]:
				headerRow=int(v)
			elif a in ["-f","--format"]:
				format=v
				if format not in formats:
					print >> stderr,"Error: format",format,"not found"
					usageExit(programName)
			elif a in ["-s","--sort"]:
				sort=True
			elif a in ["-c","--condense"]:
				condense=True
			elif a in ["-n","--not"]:
				complement=True

		startRow=headerRow+1
		#headerRow-=1
		header,prestarts=getHeader(fileName,headerRow,startRow,fs)
		
		idCols=getCol0ListFromCol1ListStringAdv(header,colString)
		
		if complement:
			cidCols=[]
			ncols=len(header)
			for i in range(0,ncols):
				if i not in idCols:
					cidCols.append(i)
			
			idCols=cidCols
			
		if sort:
			idCols.sort()
		
		outputs=[]
		
		
		
		if condense:
			condensed=condenseNumbers(idCols)
			#print >> stderr,condensed
			for blockStart,blockEnd in condensed:
				if blockStart==blockEnd:
					if format=="col0":
						outputs.append(str(blockStart))
					elif format=="col1":
						outputs.append(str(blockStart+1))
					elif format=="name":
						outputs.append(header[blockStart])
					elif format=="excel":
						outputs.append(excelColIndex(blockStart))				
				else:
					if format=="col0":
						outputs.append(str(blockStart)+condense_sep+str(blockEnd))
					elif format=="col1":
						outputs.append(str(blockStart+1)+condense_sep+str(blockEnd+1))
					elif format=="name":
						outputs.append(header[blockStart]+condense_sep+header[blockEnd])
					elif format=="excel":
						outputs.append(excelColIndex(blockStart)+condense_sep+excelColIndex(blockEnd))								
		else:	
			for id0 in idCols:
				if format=="col0":
					outputs.append(str(id0))
				elif format=="col1":
					outputs.append(str(id0+1))
				elif format=="name":
					outputs.append(header[id0])
				elif format=="excel":
					outputs.append(excelColIndex(id0))
			
		print >> stdout, ofs.join(outputs)

