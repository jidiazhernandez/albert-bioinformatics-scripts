#!/usr/bin/env python

from math import *
from sys import *
from getopt import getopt
from albertcommon import *

def log2(x):
	return log(x,2)

def printUsageAndExit(programName):
	print >> stderr,programName,"matrix  [--rows rows (format start-[end] Default: 2-)|--cols columns (Default:2-_1)|-c conditional|-o conditional-operation|-O non-conditional-operation|-v conditional value|-V non-conditional-value] ... "
	print >> stderr,"Variables:"
	print >> stderr,"ROW:current row number based 1"
	print >> stderr,"COL:current col number based 1"
	print >> stderr,"HEADERS:header array based 0"
	print >> stderr,"FIELDS:current field array based 0"
	print >> stderr,"ROWNAME:FIELDS[0]"
	print >> stderr,"COLNAME:HEADERS[COL-1]"
	print >> stderr,"X:current field FIELDS[COL-1]"
	explainColumns(stderr)
	exit(1)

if __name__=='__main__':
	programName=argv[0]
	opts,args=getopt(argv[1:],'c:o:O:v:V:',['cols=','rows='])
	
	try:
		filename,=args
	except:
		printUsageAndExit(programName)
	
	headerRow=1	
	startRow=2
	
	operations=[]
	
	currentConditional="True"
	currentColumns="2-_1"
	currentRows="2-"
	fs="\t"
	
	
	for o,v in opts:
		if o=='--cols':
			currentColumns=v
		#elif o=='--start-row':
			#startRow=int(startRow)
		elif o=='-c':
			currentConditional=v
		elif o=='-o':
			operations.append([currentColumns,currentRows,currentConditional,v])
		elif o=='-O':
			operations.append([currentColumns,currentRows,"True",v])
		elif o=='-v':
			operations.append([currentColumns,currentRows,currentConditional,"'"+v+"'"])
		elif o=='-V':
			operations.append([currentColumns,currentRows,"True","'"+v+"'"])

		elif o=='--rows':
			currentRows=v
	
	HEADERS,prestarts=getHeader(filename,headerRow,startRow,fs)
	
	minRow=None
	maxRow=None
	
	for i in range(0,len(operations)):
		columns,rows,conditional,operation=operations[i]
		rows=rows.split("-")
		if rows[0]=="":
			rowStart=1
		else:
			rowStart=int(rows[0])
		

		
		if len(rows)==1:
			rowEnd=rowStart
		else:
			if rows[1]=="":
				rowEnd=-1
				
			else:
				rowEnd=int(rows[1])
		
		
		if i==0:
			minRow=rowStart
			maxRow=rowEnd
		else:	
			minRow=min(rowStart,minRow)		
			if maxRow!=-1:
				maxRow=max(rowEnd,maxRow)
		
		rows=(rowStart,rowEnd)	
		columns=getCol0ListFromCol1ListStringAdv(HEADERS,columns)
		operations[i][0]=columns
		operations[i][1]=rows
		
		
	
	ROW=0
	fil=open(filename)
	for lin in fil:
		ROW+=1
		lin=lin.rstrip("\r\n")
		FIELDS=lin.split(fs)
		

		
		if ROW>=minRow and (maxRow==-1 or ROW<=maxRow):
			for columns,rows,conditional,operation in operations:
				
				if ROW<rows[0] or (rows[1]!=-1 and ROW>rows[1]):
					#out of range
					continue
				
				for column in columns:
					COLUMN=column+1
					ROWNAME=FIELDS[0]
					COLNAME=HEADERS[column]
					X=FIELDS[column]
					if eval(conditional):
						try:
							FIELDS[column]=eval(operation)
						except:
							if "." in X:
								X=float(X)
							else:
								X=int(X)
							FIELDS[column]=eval(operation)
								
		print >> stdout,"\t".join(toStrList(FIELDS))
		
	fil.close()
	