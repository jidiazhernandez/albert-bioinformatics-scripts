#!/usr/bin/python

from sys import *

if __name__=='__main__':
	programName=argv[0]
	args=argv[1:]
	try:
		filename,=args
	except:
		print >> stderr,programName,"fastqfilename"
		exit()
		
	lino=0	
	
	minO=100000
	maxO=-100000
	
	minSeqL=100000
	maxSeqL=0
	isFasta=False
	
	fil=open(filename)
	for lin in fil:
		lin=lin.strip()
		if len(lin)<1:
			continue
		
		lino+=1
		if lino%4==1:

			if lin[0] not in ["@",">"]:

					
				print >> stderr,"wrong format @|>",lino,lin
				exit()
			elif lin[0]=='>':
				isFasta=True
		
		if isFasta:
			if lino%2==0:
				seq=lin
				lseq=len(seq)
				maxSeqL=max(lseq,maxSeqL)
				minSeqL=min(lseq,minSeqL)
		else:
			if lino%4==2: #seq
				seq=lin
				lseq=len(seq)
				maxSeqL=max(lseq,maxSeqL)
				minSeqL=min(lseq,minSeqL)
				
				
			if lino%4==3 and lin[0]!="+":
				print >> stderr,"wrong format +",lino,lin
			
			if lino%4==0:
				for c in lin:
					ordC=ord(c)
					if ordC<minO:
						minO=ordC
						exampleLine=lin
						
					maxO=max(maxO,ordC)
					#if minO<59: #it's a sanger, no need to check further~ check anyway to get lengths	
						#print >> stderr,lin
						#print >> stderr,"sanger format"
						#print >> stdout,"SANGER\t"+lin+"\t"+"minLen=",minSeqL,";maxLen=",maxSeqL
						#exit()
					
		
				
	
	fil.close()
	
	if isFasta:
		print >> stderr,"fasta format"
		print >> stdout,"\t".join([filename,"FASTA","",str(minSeqL),str(maxSeqL)])
	else:
		if minO<59:
			print >> stderr,"line with min ord:",exampleLine
			print >> stderr,"sanger format"
			print >> stdout,"\t".join([filename,"SANGER",exampleLine,str(minSeqL),str(maxSeqL)])	
		else:	
			if minO<64:
				print >> stderr,"line with min ord:",exampleLine
				print >> stderr,"either (more likely) solexa, or sanger format"
				print >> stdout,"\t".join([filename,"SOLEXA|SANGER",exampleLine,str(minSeqL),str(maxSeqL)]) #filename+"\tSOLEXA|SANGER\t"+exampleLine+"\t"+"minLen=",minSeqL,";maxLen=",maxSeqL
			else:
				print >> stderr,"line with min ord:",exampleLine
				print >> stderr,"most likely illumina/solexa-1.3+, although solexa or sanger format cannot be ruled out"
				print >> stdout,"\t".join([filename,"ILLUMINASOLEXA1.3+|SOLEXA|SANGER",exampleLine,str(minSeqL),str(maxSeqL)]) #filename+"\tILLUMINASOLEXA1.3+|SOLEXA|SANGER\t"+exampleLine+"\t"+"minLen=",minSeqL,";maxLen=",maxSeqL
		
	