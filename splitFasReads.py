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

#split read into x bp, discarding <x bp reads

from sys import *

def outputSeq(seqstruct,splitlength):
	#print >> stderr,seqstruct
	tag,seq,qual,state=seqstruct
	outI=0
	
	if len(qual)>0 and len(seq)>0 and len(qual)!=len(seq):
		print >> stderr,"error: seq is not same length as qual string"
		exit()
	
	if len(seq)>=splitlength:
		for i in range(0,len(seq),splitlength):
			if i+splitlength<=len(seq):
				outI+=1
				thisTag=tag+"_"+str(outI)
				
				if len(qual)>0:
					print >> stdout,"@"+thisTag #this is a fastq
				else:
					print >> stdout,">"+thisTag #this is a fasta
				
				print >> stdout,seq[i:i+splitlength]
				
				if len(qual)>0:
					print >> stdout,"+"
					print >> stdout,qual[i:i+splitlength]
				
	#reinit seqstruct
	seqstruct[0]=""
	seqstruct[1]=""
	seqstruct[2]=""
	seqstruct[3]=0

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	
	try:
		filename,splitlength=args
	except:
		print >> stderr,programName,"filename splitlength"
		exit()
	splitlength=int(splitlength)
	seqstruct=["","","",-1] #tag,seq,qual
	
	lino=0
	
	fil=open(filename)
	for lin in fil:
		lin=lin.rstrip("\r\n")
		if len(lin)==0:
			continue
			
		lino+=1
			
		if lino%2==1:
			if lin[0] in ['>','@']:
				outputSeq(seqstruct,splitlength)
				seqstruct[0]=lin[1:]
			elif lin[0] in ["+"]:
				seqstruct[3]=1
			else:
				print >> stderr,"invalid formating at",lino,lin
		else:
			if seqstruct[3]==0:
				#get sequence
				seqstruct[1]+=lin
			else:
				#get quality string
				seqstruct[2]+=lin			
		
		
	fil.close()
	
	#output the last bit
	outputSeq(seqstruct,splitlength)
	
