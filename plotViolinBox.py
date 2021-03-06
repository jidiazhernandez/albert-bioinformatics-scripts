#!/usr/bin/env python
import warnings
warnings.filterwarnings("ignore")
#derived from plotExpBox2.py
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

from pylab import *
from sys import stderr,stdout,argv
from getopt import getopt
import sys
from albertcommon import *
from welchttest import welchs_approximate_ttest_arr
from scipy.stats.stats import ttest_ind,ttest_1samp,mannwhitneyu
from scipy.stats import wilcoxon,ansari,fligner,levene,bartlett 
from glob import glob
from random import *
from PZFXMaker import *
from scipy.stats import gaussian_kde,histogram
from numpy import arange
import traceback
import numpy
from math import log

def divideDataPerCols(data,thresholds):  # [||]
	dividedDataMain=[]
	lent=len(thresholds)
	for i in range(0,lent+1):
		dividedDataMain.append([])
	
	for i in range(0,len(data)):	#go thru the columns	
		curCol=data[i]
		for j in range(0,len(thresholds)+1):
			dividedDataMain[j].append([])
		
		for x in curCol:
			#now classifies
			k=-1
			if x<thresholds[0]:
				k=0
			elif x>=thresholds[lent-1]:
				k=lent
			else:
				for j in range(0,lent-1):
					if x>=thresholds[j] and x<thresholds[j+1]:
						k=j+1
						
					
			dividedDataMain[k][i].append(x)

	return dividedDataMain
	
def plotExpBox(data,xtickLabels,showIndPoints,mark,markMean,showMean,notch,whisker,outliers,xlegendrotation,xlabe,ylabe,titl,showSampleSizes,showViolin,showBox,annot,trendData,plotItemLegend,makePzfxFile,makeBinMatrix,dividePlots):
	
	#fig=plt.figure()
	if plotItemLegend:
		ax2=subplot(122)
		ax=subplot(121)
	else:
		ax=gca()
		
	
	
	prevHoldState=ishold()	
	hold(True)
	
	if outliers:	
		fliers="b+"
	else:
		fliers=""

	whisValue=0.0

	if whisker:
		whisValue=1.5

	for axhlin in axhlines:
		#print axhlin
		linw=1
		try:
			linw=float(axhlin[3])
		except:
			pass
		axhline(float(axhlin[0]),linestyle=axhlin[1],color=axhlin[2],linewidth=linw)

	
	if len(dividePlots)>0: #make divided matrices
		dataDP=divideDataPerCols(data,dividePlots)
	
	##for i in range(0,len(data)):
	##	print >> stderr,len(data[i])

	if showBox:
		if len(dividePlots)==0:
			boxplotted=ax.boxplot(data,notch,widths=0.5,sym=fliers,whis=whisValue)
			#setp(boxplotted["boxes"],color="blue")
			whiskerlines=boxplotted["whiskers"]
			for w in whiskerlines:
				w.set_linestyle(whiskerStyle)
		else:
			for datdp in dataDP:
				boxplotted=ax.boxplot(datdp,notch,widths=0.5,sym=fliers,whis=whisValue)
				#setp(boxplotted["boxes"],color="blue")
				whiskerlines=boxplotted["whiskers"]
				for w in whiskerlines:
					w.set_linestyle(whiskerStyle)			
	
	
	#w.set_linewidth(5)		
	#print >> stderr,resultD
	
	maxMax=-10000000.0
	minMin=10000000.0
	
	violinw=min(0.15*max(len(data)-1,1.0),0.5)

	if trendData:
		#print >> stderr,"plot"
		for trendDataStartIdx,trendDataForThisStartIdx in trendData.items():
			#print >> stderr,"plot",len(trendDataForThisStartIdx)
			trendcurves=[]
			legendlabels=[]
			if annot:
				annotForThisStartIdx=annot[trendDataStartIdx]
			for i in range(0,len(trendDataForThisStartIdx)):
				trendDataPerItem=trendDataForThisStartIdx[i]
				if annot:
					annotThisItem=annotForThisStartIdx[i]
				if trendDataPerItem:
					#print >> stderr,"plot"
					thisTrend=ax.plot(range(trendDataStartIdx+1,trendDataStartIdx+len(trendDataPerItem)+1),trendDataPerItem,"-")
					if annot and plotItemLegend:
						trendcurves.append(thisTrend)
						legendlabels.append(annotThisItem)
	
		
	for i in range(0,len(data)):
		curCol=data[i]
#		datasorted=data[:]
#		datasorted.sort()
#		numData=len(datasorted)
#		HQn=numData*3/4		
#		LQn=numData*1/4
#		maxMax=max(maxMax,datasorted[HQn]*1.5)
#		minMin=min(minMax,datasorted[LQn]*1.5)
			
		maxMax=max(maxMax,max(curCol))
		minMin=min(minMin,min(curCol))
		if showMean:
			ax.plot([i+0.75,i+1.25],[mean(curCol)]*2,markMean)
		
		
				

		if showViolin:
			if len(dividePlots)==0:
				kernel=gaussian_kde(curCol)
				kernel_min=kernel.dataset.min()
				kernel_max=kernel.dataset.max()
				violinx=arange(kernel_min,kernel_max,(kernel_max-kernel_min)/100.) 
				violinv=kernel.evaluate(violinx)
				violinv=violinv/violinv.max()*violinw
				fill_betweenx(violinx,i+1,violinv+i+1,facecolor=vfacecolor,alpha=valpha) #'y', 0.3
				fill_betweenx(violinx,i+1,-violinv+i+1,facecolor=vfacecolor,alpha=valpha)
			else:
				for j in range(0,len(dataDP)):
					curcoldp=dataDP[j][i]
					if len(curcoldp)<2:
						continue
					kernel=gaussian_kde(curcoldp)
					kernel_min=kernel.dataset.min()
					kernel_max=kernel.dataset.max()
					violinx=arange(kernel_min,kernel_max,(kernel_max-kernel_min)/100.) 
					violinv=kernel.evaluate(violinx)
					violinv=violinv/violinv.max()*violinw
					fill_betweenx(violinx,i+1,violinv+i+1,facecolor=vfacecolor,alpha=valpha) #'y', 0.3
					fill_betweenx(violinx,i+1,-violinv+i+1,facecolor=vfacecolor,alpha=valpha)										
		if showIndPoints:
			plot([i+1]*len(curCol),curCol,mark)
			
	if showSampleSizes:
		if len(dividePlots)==0:
			for i in range(0,len(data)):
				curCol=data[i]
				text(i+1,maxMax*1.05,str(len(curCol)),horizontalalignment='center',verticalalignment='center',color='red')
		else:
			for i in range(0,len(data)):
				thisL=[]
				for j in range(0,len(dataDP)):
					thisL.append(len(dataDP[j][i]))
				
				sumL=sum(thisL)
				text(i+1,maxMax*1.05,"+".join([str(x) for x in thisL])+"="+str(sumL),horizontalalignment='center',verticalalignment='center',color='red')
					
	
	
	xticks( range(1,len(data)+1), xtickLabels , rotation=xlegendrotation)
	
	if makeBinMatrix:
		binMatrixOutFilename,binMatrixNumBins=makeBinMatrix
		outputBinFiles(binMatrixOutFilename,data,xtickLabels,minMin,maxMax,binMatrixNumBins)
	
	if makePzfxFile:
		
		
		pzfxTemplateFile,outFile,tableRefID=makePzfxFile
		#prepare data format
		PzfxData=[]
		for xtickLabel,dataCol in zip(xtickLabels,data):
			PzfxData.append( [xtickLabel, dataCol ] )
		writePzfxTableFile(outFile,pzfxTemplateFile,tableRefID,titl,80,3,PzfxData)
	
	xlabel(xlabe)
	ylabel(ylabe)
	title(titl)
	if ylims:
		ylim([ylims[0],ylims[1]])
	else:
		ylim([minMin-maxMax*0.1,maxMax*1.1])
	
	
	
	if plotItemLegend:
		box=ax.get_position()
		#gcf().set_figwidth(gcf().get_figwidth()*2)
		#ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
		#subplots_adjust(top=0.8,bottom=0.1,left=0,right=0.8)
		
		#box2=ax2.get_position()
		#ax2.set_position([box2.x0,box2.y0, box.width * 0.1,box.height])
		subplots_adjust(top=0.8, bottom=0.1, left=0, right=0.8)
		leg=ax.legend(trendcurves,legendlabels,bbox_to_anchor=(1,0),loc="center left")
		#leg = gcf().get_legend()
		ltext  = leg.get_texts()
		
		
		plt.setp(ltext, fontsize=10)
	
	hold(prevHoldState)

def findIndices(needles,haystack):
	indices=[]
	for needle in needles:
		indices.append(haystack.index(needle))

	return indices

def rearrangeColAndRowSqMatrix(M,from_indices):
	newM=[]
	lenM=len(M)
	for r in range(0,lenM):
		newRow=[]
		newM.append(newRow)
		for c in range(0,lenM):
			newRow.append(M[from_indices[r]][from_indices[c]])

	return newM

def printMatrix(stream,M,prefixes):
	for row,prefix in zip(M,prefixes):
		for cell in row:
			print >> stream,"%g\t" % (cell),

				
		print >> stream,prefix
#use pvalue as a distance metric
#dist=1-pvalues
#fake the record for PyCluster
def makePValueClusterPlot(jobname,sampleNames,pvaluesM,methodCluster):



	#fake a record
	record=Record()
	#fake M
	M=[]
	Mr=[]
	M.append(Mr)
	for sample in sampleNames:
		Mr.append(0)

	record.data=numpy.array(M)
	record.mask=None
	record.geneid=["Dummy"]
	record.genename=["Dummy"]
	record.expid=sampleNames
	record.uniqid="GENENAME"

	#now do something serious
	distM=[]
	for pvalueRows in pvaluesM:
		distRow=[]
		distM.append(distRow)
		for pvalue in pvalueRows:
			distRow.append(1.0-pvalue)

	
	#now cluster
	Tree=treecluster(distancematrix=distM,method=methodCluster)	

	record.save(jobname,expclusters=Tree)

	#now hijack the result file and change it to pvalue heatmap
	fil=open(jobname+".cdt")
	firstthreelines=[]
	lino=0
	for lin in fil:
		lino+=1
		if lino>3:
			break
		lin=lin.rstrip()
		firstthreelines.append(lin)
		if lino==1:
			fields=lin.split("\t")	
			arrayOrdered=fields[3:]
	


	fil.close()

	fil=open(jobname+".cdt","w")
	for lin in firstthreelines:
		print >> fil, lin

	rearrangedCorrMatrix=rearrangeColAndRowSqMatrix(pvaluesM,findIndices(arrayOrdered,sampleNames))

	for i in range(0,len(arrayOrdered)):
		print >> fil, arrayOrdered[i]+"\t"+arrayOrdered[i]+"\t"+"1.000000",
		for j in range(0,len(arrayOrdered)):
			print >> fil,"\t"+str(rearrangedCorrMatrix[i][j]),

		print >> fil,""

	fil.close()
	

	fil=open(jobname+".mat","w")

	print >> fil, "Correlation Matrix (Not Clustered)"
	print >> fil,"\t".join(sampleNames)
	printMatrix(fil, pvaluesM, sampleNames)

	print >> fil, "Correlation Matrix (Clustered)"
	print >> fil,"\t".join(arrayOrdered)
	printMatrix(fil, rearrangedCorrMatrix, arrayOrdered)
	fil.close()


def makePValueRawPlot(jobname,sampleNames,pvaluesM):



	#fake a record
	record=Record()
	#fake M
	M=[]
	Mr=[]
	M.append(Mr)
	for sample in sampleNames:
		Mr.append(0)

	record.data=numpy.array(M)
	record.mask=None
	record.geneid=["Dummy"]
	record.genename=["Dummy"]
	record.expid=sampleNames
	record.uniqid="GENENAME"

	#now do something serious


	record.save(jobname)

	#now hijack the result file and change it to pvalue heatmap
	fil=open(jobname+".cdt")
	firstthreelines=[]
	lino=0
	for lin in fil:
		lino+=1
		if lino>2:
			break
		lin=lin.rstrip()
		firstthreelines.append(lin)
		if lino==1:
			fields=lin.split("\t")	
			arrayOrdered=fields[3:]
	


	fil.close()

	fil=open(jobname+".cdt","w")
	for lin in firstthreelines:
		print >> fil, lin

	rearrangedCorrMatrix=pvaluesM


	for i in range(0,len(arrayOrdered)):
		print >> fil, arrayOrdered[i]+"\t"+arrayOrdered[i]+"\t"+"1.000000",
		for j in range(0,len(arrayOrdered)):
			print >> fil,"\t"+str(rearrangedCorrMatrix[i][j]),

		print >> fil,""

	fil.close()
	



def trimData(plotData,size):
	for plotDataVector in plotData:
		shuffle(plotDataVector)
		del plotDataVector[size:len(plotDataVector)]


def drawHistogram(outfilename,plotData,xtickLabels,nbins=50):
	fig=figure(figsize=(8,len(plotData)*2))
	fig.subplots_adjust(top=0.8, bottom=0.1, left=0.2, right=0.8)
	
	#find minmin and maxmax for plotData
	minmin=min(plotData[0])
	maxmax=max(plotData[0])
	
	for i in range(1,len(plotData)):
		minmin=min(minmin,min(plotData[i]))
		maxmax=max(maxmax,max(plotData[i]))
	
	rangedata=maxmax-minmin
	#maxmax+=rangedata/float(nbin)
	#minmin-=rangedata/float(nbin)
	maxy=0
	
	axes=[]
	
	for i,D,label in zip(range(0,len(plotData)),plotData,xtickLabels):
		ax = fig.add_subplot(len(plotData),1,i+1) #len(plotData),1,i #i+1 in place of i (6/18/2012)
		__n,__bins,__patches=ax.hist(D,nbins,(minmin,maxmax),True,histtype="stepfilled")
		#ax.plot(__bins,__n,'r-')
		maxy=max(maxy,max(__n))
		ax.set_title(label)
		density = gaussian_kde(D)
		xs = np.linspace(minmin,maxmax,200)
		density.covariance_factor = lambda : .25
		density._compute_covariance()
		ax.plot(xs,density(xs))
		#ax.set_xlim(minmin,maxmax)
		#ax.set_ylim(0,maxy)
		axes.append(ax)
	#fig.show()
	
	for ax in axes:
		ax.set_ylim(0,maxy*1.1)

	fig.savefig(outfilename,bbox_inches="tight")

def drawDensigram(outfilename,plotData,xtickLabels,nbins=50):
	fig=figure(figsize=(8,len(plotData)*2))
	fig.subplots_adjust(top=0.8, bottom=0.1, left=0.2, right=0.8)
	
	#find minmin and maxmax for plotData
	minmin=min(plotData[0])
	maxmax=max(plotData[0])
	
	for i in range(1,len(plotData)):
		minmin=min(minmin,min(plotData[i]))
		maxmax=max(maxmax,max(plotData[i]))
	
	rangedata=maxmax-minmin
	#maxmax+=rangedata/float(nbin)
	#minmin-=rangedata/float(nbin)
	maxy=0
	
	axes=[]
	
	for i,D,label in zip(range(0,len(plotData)),plotData,xtickLabels):
		ax = fig.add_subplot(len(plotData),1,i+1) #len(plotData),1,i #i+1 in place of i (6/18/2012)

		
		ax.set_title(label)
		density = gaussian_kde(D)
		xs = np.linspace(minmin,maxmax,200)
		density.covariance_factor = lambda : .25
		density._compute_covariance()
		ax.plot(xs,density(xs))

		axes.append(ax)
	

	fig.savefig(outfilename,bbox_inches="tight")


def outputBinFiles(outfilename,plotData,xtickLabels,minMin,maxMax,nbins=50):
	
	histoArrays=[]
	
	_low_range=-100
	_binsize=-100
	_extrapoints=-1
	for col,xtickLabel in zip(plotData,xtickLabels):
		histoArray,low_range,binsize,extrapoints=histogram(col,numbins=nbins,defaultlimits=(minMin,maxMax))
		histoArrays.append(histoArray)
		
		if _binsize==-100:
			_binsize=binsize
			_low_range=low_range
		else:
			if _binsize!=binsize or low_range!=_low_range:
				print >> stderr,"inconsistent histo",_binsize,_low_range,histoArray,low_range,binsize,extrapoints
				exit(1)
				
		
		if extrapoints>0:
			print >> stderr,"extrapoints>0",histoArray,low_range,binsize,extrapoints
			exit(1)
	
	binLows=[]
	
	for i in range(0,nbins):
		binLows.append(i*binsize)
	
	outfil=open(outfilename,"w")
	outv=["bins"]
	for binLow in binLows:
		outv.append(str(binLow))
	
	print >> outfil,"\t".join(outv)

	#now the data
	for xtickLabel,histoArray in zip(xtickLabels,histoArrays):
		outv=[xtickLabel]
		totalPoint=sum(histoArray)
		for v in histoArray:
			outv.append(str(float(v)/totalPoint))
	
		print >> outfil,"\t".join(outv)
			
	outfil.close()
	
def filterDataInRangeInclusive(D,mi,ma):
	xd=[]
	N=0
	NIN=0
	NBelow=0
	NAbove=0
	for d in D:
		N+=1
		if mi!=None and d<mi:
			NBelow+=1
			continue
		if ma!=None and d>ma:
			NAbove+=1
			continue
		xd.append(d)
		NIN+=1
	
	return xd,N,NIN,NBelow,NAbove

def writeXYZPvalues(filename,xtickLabels,pvalueM):
	fil=open(filename,"w")
	for x in range(0,len(xtickLabels)):
		for y in range(0,len(xtickLabels)):
			print >> fil,xtickLabels[x]+"\t"+str(xtickLabels[y])+"\t"+str(pvalueM[x][y])
	fil.close()


def mean2(X):
	return float(sum(X))/len(X)
			
def plotExpBox_Main(inputFiles,headers,valcols,outputFile,sep,startRow,showIndPoints,mark,markMean,showMean,notch,whisker,outliers,plotPvalueCluster,outputClusterPrefix,methodCluster,xlegendrotation,xlabe,ylabe,figsz,titl,showSampleSizes,trimToMinSize,relabels,logb,plotHistogramToFile,plotMedianForGroups,botta,showViolin,showBox,firstColAnnot,plotTrend,showLegend,makePzfxFile,makeBinMatrix,writeDataSummaryStat,summaryStatRange,minuslog10pvalue,minNDataToKeep,vfacecolor,valpha,outXYZPvalues,dividePlots):

	#if plotPvalueCluster:
		#if pvalue cluster is needed:
	#	from Bio.Cluster.cluster import *
	#	from Bio.Cluster import *
		#endif


	
	#the real deal!
	plotData=[]	
	xtickLabels=[]
	
	trendData={}
	annot={}
	
	minSize=-1

	for inputFile,header,cols in zip(inputFiles,headers,valcols):
		fin=generic_istream(inputFile)
		
		startIdx=len(plotData)
		
		if firstColAnnot:
			colAnnot=cols[0]
			cols=cols[1:]
			annotThisFile=[]
			annot[startIdx]=annotThisFile
		else:
			colAnnot=-1
			annotThisFile=None
			
		for col in cols:
			plotData.append([])
			xtickLabels.append(header[col])

		colIndices=range(startIdx,startIdx+len(cols))
		
		if plotTrend:
			#print >> stderr,"plotTrend"
			trendDataThisFile=[]
			trendData[startIdx]=trendDataThisFile
		else:
			trendDataThisFile=None
			
			
		lino=0
		for lin in fin:
			lino+=1
			if lino<startRow:
				continue		
			fields=lin.rstrip("\r\n").split(sep)
			
			if plotTrend:
				#print >> stderr,"a"
				trendDataThisLine=[]
			else:
				trendDataThisLine=None
			
			allDataOKThisLine=True
			
			if colAnnot>=0:
				annotThisFile.append(fields[colAnnot])
			
			for idx,col in zip(colIndices,cols):
				try:
					value=float(fields[col])
					if logb!=0:
						if value==0.0:
							raise ValueError
						value=log(value)/logb							
					plotData[idx].append(value)
					
					if plotTrend:
						trendDataThisLine.append(value)
						#print >> stderr,"value:",value
					
				except:
					allDataOKThisLine=False	
				
			if plotTrend:
				if allDataOKThisLine:
					trendDataThisFile.append(trendDataThisLine)
				else:
					trendDataThisFile.append(None)
			
		fin.close()
	
		
		if minSize==-1:
			minSize=len(plotData[idx]) #or startIDX?
		else:
			minSize=min([minSize,len(plotData[idx])])
		

	if trimToMinSize:
		print >> stderr,"trimming to min size =",minSize
		trimData(plotData,minSize)

	if len(relabels)>0:
		#if len(relabels)!=len(xtickLabels):
		#	print >> stderr,"relabels doesn't have the same length as original label vectors",xtickLabels,"=>",relabels
		#	exit()
		print >> stderr,xtickLabels
		print >> stderr,relabels
		for i,relabel in zip(range(0,len(relabels)),relabels):
			xtickLabels[i]=relabel
		
	
	for i in range(0,len(plotMedianForGroups)):
		plotMedianForGroups[i]=getCol0ListFromCol1ListStringAdv(xtickLabels,plotMedianForGroups[i])
			
	
	#drawing medians:
	medianToDraw=[]
	for mediangrouper in plotMedianForGroups:
		curD=[]		
		for c in mediangrouper:
			curD.extend(plotData[c])
		medianToDraw.append(median(curD))


	for c in range(len(plotData)-1,-1,-1):
		if len(plotData[c])<minNDataToKeep:
			print >> stderr,xtickLabels[c],"discarded because has only",len(plotData[c]),"data points <",minNDataToKeep
			del plotData[c]
			del xtickLabels[c]

	if not skipStat:
		print >> stdout,"student t-test (1 sample; mean=0)"
		print >> stdout,"sample","mean","p-val","median"
	
		if writeDataSummaryStat:
			fDSS=open(writeDataSummaryStat,"w")
			print >> fDSS,"sample\tmean\tvar\tsd\tmin\tmax\tN\tNInRange["+str(summaryStatRange[0])+","+str(summaryStatRange[1])+"]\t%NInRange\tNbelowRange\t%Nbelow\tNAboveRange\t%NAbove"
			
		for x in range(0,len(plotData)):
			#print >> stderr, len(plotData[x])
			try:
				print >> stdout, xtickLabels[x],mean(plotData[x]),ttest_1samp(plotData[x],0)[1],median(plotData[x])
			except:
				print >> stdout, xtickLabels[x],mean(plotData[x]),"NA",median(plotData[x])
			
			if writeDataSummaryStat:
				sumData,N,NIN,NBelow,NAbove=filterDataInRangeInclusive(plotData[x],summaryStatRange[0],summaryStatRange[1])
				
				if NIN>1:
					#print >> stderr,"sumData=",sumData
					#print >> stderr,mean
					mea=mean2(sumData)
					DDOF=1
					sd=std(sumData,ddof=DDOF)
					var=sd*sd
					mi=min(sumData)
					ma=max(sumData)
				else:
					mea="NA"
					sd="NA"
					var="NA"
					mi="NA"
					ma="NA"
				
			
					
				print >> fDSS,xtickLabels[x]+"\t"+str(mea)+"\t"+str(var)+"\t"+str(sd)+"\t"+str(mi)+"\t"+str(ma)+"\t"+str(N)+"\t"+str(NIN)+"\t"+str(float(NIN)*100/N)+"\t"+str(NBelow)+"\t"+str(float(NBelow)*100/N)+"\t"+str(NAbove)+"\t"+str(float(NAbove)*100/N)
			
	
		pvalueM=[]
		
		if writeDataSummaryStat:
			fDSS.close()
		
		print >> stdout,""
		
		print >> stdout,"student t-test (2 samples)"
		print >> stdout,"p-val",
		for x in range(0,len(plotData)):
			print >> stdout,xtickLabels[x],
		
		print >> stdout,""
	
		for x in range(0,len(plotData)):
			pvalueRow=[]
			pvalueM.append(pvalueRow)
			print >> stdout, xtickLabels[x],
			for y in range(0,len(plotData)):
				if y<=x:
					print >> stdout, "",
					if x==y:
						if minuslog10pvalue:
							pvalueRow.append(0.0)
						else:
							pvalueRow.append(1.0)
					else:
						pvalueRow.append(pvalueM[y][x])
				else:
					try:
						pvalue=ttest_ind(plotData[x],plotData[y])[1]
					except:
						pvalue=1.0
					
					if minuslog10pvalue and str(pvalue)!="NA":
						try:
							pvalue=-1*log(pvalue,10)
						except:
							pvalue=-1000.0
					
					print >> stdout, str(pvalue),
					pvalueRow.append(pvalue)
			print >> stdout,"";	
	
		
		print >> stdout,""
	
		
	
	
		if plotPvalueCluster:
			makePValueRawPlot(outputClusterPrefix+"_t_raw",xtickLabels,pvalueM)
			makePValueClusterPlot(outputClusterPrefix+"_t",xtickLabels,pvalueM,methodCluster)
	
	
			
		pvalueM=[]
	
		print >> stdout,"welch t-test"
		print >> stdout,"p-val",
		for x in range(0,len(plotData)):
			print >> stdout,xtickLabels[x],
		
		print >> stdout,""
		for x in range(0,len(plotData)):
			pvalueRow=[]
			pvalueM.append(pvalueRow)
			print >> stdout, xtickLabels[x],
			for y in range(0,len(plotData)):
				if y<=x:
					print >> stdout, "",
					if x==y:
						if minuslog10pvalue:
							pvalueRow.append(0.0)
						else:
							pvalueRow.append(1.0)
					else:
						pvalueRow.append(pvalueM[y][x])
						
				else:
					try:
						pvalue=welchs_approximate_ttest_arr(plotData[x],plotData[y])[3]
					except:
						pvalue=1.0
	
					if minuslog10pvalue and str(pvalue)!="NA":
						try:
							pvalue=-1*log(pvalue,10)
						except:
							pvalue=-1000.0
	
					
					print >> stdout, str(pvalue),
					pvalueRow.append(pvalue)
			print >> stdout,"";
	
		if outXYZPvalues:
			writeXYZPvalues(outXYZPvalues+"_Welch.xyz",xtickLabels,pvalueM)
	
		if plotPvalueCluster:
			makePValueRawPlot(outputClusterPrefix+"_Welch_raw",xtickLabels,pvalueM)
			makePValueClusterPlot(outputClusterPrefix+"_Welch",xtickLabels,pvalueM,methodCluster)
	
		
		print >> stdout,""
		print >> stdout,"non-parametric (Mann-Whitney U)" #"non-parametric (Mann-Whitney U if larger n<=20 else Wilcoxon)"
		print >> stdout,"p-val",
		for x in range(0,len(plotData)):
			print >> stdout,xtickLabels[x],
		
	
		pvalueM=[]
	
		print >> stdout,""
		for x in range(0,len(plotData)):
			pvalueRow=[]
			pvalueM.append(pvalueRow)
			print >> stdout, xtickLabels[x],
			for y in range(0,len(plotData)):
				if y<=x:
					print >> stdout, "",
					if x==y:
						if minuslog10pvalue:
							pvalueRow.append(0.0)
						else:
							pvalueRow.append(1.0)
					else:
						pvalueRow.append(pvalueM[y][x])
				else:
					#if max(len(plotData[x]),len(plotData[y]))<=20:
					try:
						pvalue=mannwhitneyu(plotData[x],plotData[y])[1]*2				
					except:
						pvalue=1.0
	
					if minuslog10pvalue and str(pvalue)!="NA":
						try:
							pvalue=-1*log(pvalue,10)
						except:
							pvalue=-1000.0
	
	
					print >> stdout,pvalue, #mann-whiteney need to mul by 2 (one tail to two tail)
					pvalueRow.append(pvalue)
					#else:
					#	print >>  stdout,wilcoxon(plotData[x],plotData[y])[1], # this is two-tailed already stdout, "", #
			print >> stdout,"";	
	
		if outXYZPvalues:
			writeXYZPvalues(outXYZPvalues+"_U.xyz",xtickLabels,pvalueM)
		
	
		if plotPvalueCluster:
			makePValueRawPlot(outputClusterPrefix+"_U_raw",xtickLabels,pvalueM)
			makePValueClusterPlot(outputClusterPrefix+"_U",xtickLabels,pvalueM,methodCluster)
		
		#####now the variance tests
		
		print >> stdout,""
		print >> stdout,"Ansari-Bradley Two-sample Test for difference in scale parameters " 
		print >> stdout,"p-val",
		
		
		for x in range(0,len(plotData)):
			print >> stdout,xtickLabels[x],
		
	
		pvalueM=[]
	
		print >> stdout,""
		for x in range(0,len(plotData)):
			pvalueRow=[]
			pvalueM.append(pvalueRow)
			print >> stdout, xtickLabels[x],
			for y in range(0,len(plotData)):
				if y<=x:
					print >> stdout, "",
					if x==y:
						if minuslog10pvalue:
							pvalueRow.append(0.0)
						else:
							pvalueRow.append(1.0)
					else:
						pvalueRow.append(pvalueM[y][x])
				else:
					#if max(len(plotData[x]),len(plotData[y]))<=20:
					try:
						pvalue=ansari(plotData[x],plotData[y])[1]		
					except:
						pvalue="NA"
	
					if minuslog10pvalue and str(pvalue)!="NA":
						try:
							pvalue=-1*log(pvalue,10)
						except:
							pvalue=-1000.0
	
	
						#pvalue=1.0
					print >> stdout,pvalue,
					pvalueRow.append(pvalue)
					#else:
					#	print >>  stdout,wilcoxon(plotData[x],plotData[y])[1], # this is two-tailed already stdout, "", #
			print >> stdout,"";	
		
		if plotPvalueCluster:
			makePValueRawPlot(outputClusterPrefix+"_Ansari_raw",xtickLabels,pvalueM)
			makePValueClusterPlot(outputClusterPrefix+"_Ansari",xtickLabels,pvalueM,methodCluster)	
		
		
		#####
	
		#####now the variance tests
		
		print >> stdout,""
		print >> stdout,"Fligner's Two-sample Test for equal variance (non-parametrics)" 
		print >> stdout,"p-val",
		
		
		for x in range(0,len(plotData)):
			print >> stdout,xtickLabels[x],
		
	
		pvalueM=[]
	
		print >> stdout,""
		for x in range(0,len(plotData)):
			pvalueRow=[]
			pvalueM.append(pvalueRow)
			print >> stdout, xtickLabels[x],
			for y in range(0,len(plotData)):
				if y<=x:
					print >> stdout, "",
					if x==y:
						if minuslog10pvalue:
							pvalueRow.append(0.0)
						else:
							pvalueRow.append(1.0)
					else:
						pvalueRow.append(pvalueM[y][x])
				else:
					#if max(len(plotData[x]),len(plotData[y]))<=20:
					try:
						pvalue=fligner(plotData[x],plotData[y])[1]		
					except:
						pvalue="NA"
						#pvalue=1.0
						
					if minuslog10pvalue and str(pvalue)!="NA":
						try:
							pvalue=-1*log(pvalue,10)
						except:
							pvalue=-1000.0
	
	
					print >> stdout,pvalue,
					pvalueRow.append(pvalue)
					#else:
					#	print >>  stdout,wilcoxon(plotData[x],plotData[y])[1], # this is two-tailed already stdout, "", #
			print >> stdout,"";	
		
		if plotPvalueCluster:
			makePValueRawPlot(outputClusterPrefix+"_fligner_raw",xtickLabels,pvalueM)
			makePValueClusterPlot(outputClusterPrefix+"_fligner",xtickLabels,pvalueM,methodCluster)	
		
		
		#####
	
		#####now the variance tests
		
		print >> stdout,""
		print >> stdout,"Levene's Two-sample Test for equal variance" 
		print >> stdout,"p-val",
		
		
		for x in range(0,len(plotData)):
			print >> stdout,xtickLabels[x],
		
	
		pvalueM=[]
	
		print >> stdout,""
		for x in range(0,len(plotData)):
			pvalueRow=[]
			pvalueM.append(pvalueRow)
			print >> stdout, xtickLabels[x],
			for y in range(0,len(plotData)):
				if y<=x:
					print >> stdout, "",
					if x==y:
						if minuslog10pvalue:
							pvalueRow.append(0.0)
						else:
							pvalueRow.append(1.0)
					else:
						pvalueRow.append(pvalueM[y][x])
				else:
					#if max(len(plotData[x]),len(plotData[y]))<=20:
					try:
						pvalue=levene(plotData[x],plotData[y])[1]		
					except:
						pvalue="NA"
						#pvalue=1.0
						
					if minuslog10pvalue and str(pvalue)!="NA":
						try:
							pvalue=-1*log(pvalue,10)
						except:
							pvalue=-1000.0
	
	
					print >> stdout,pvalue,
					pvalueRow.append(pvalue)
					#else:
					#	print >>  stdout,wilcoxon(plotData[x],plotData[y])[1], # this is two-tailed already stdout, "", #
			print >> stdout,"";	
		
		if plotPvalueCluster:
			makePValueRawPlot(outputClusterPrefix+"_levene_raw",xtickLabels,pvalueM)
			makePValueClusterPlot(outputClusterPrefix+"_levene",xtickLabels,pvalueM,methodCluster)	
		
		
		#####
	
		#####now the variance tests
		
		print >> stdout,""
		print >> stdout,"Bartlett's Two-sample Test for equal variance (for normal distributions)" 
		print >> stdout,"p-val",
		
		
		for x in range(0,len(plotData)):
			print >> stdout,xtickLabels[x],
		
	
		pvalueM=[]
	
		print >> stdout,""
		for x in range(0,len(plotData)):
			pvalueRow=[]
			pvalueM.append(pvalueRow)
			print >> stdout, xtickLabels[x],
			for y in range(0,len(plotData)):
				if y<=x:
					print >> stdout, "",
					if x==y:
						if minuslog10pvalue:
							pvalueRow.append(0.0)
						else:
							pvalueRow.append(1.0)
					else:
						pvalueRow.append(pvalueM[y][x])
				else:
					#if max(len(plotData[x]),len(plotData[y]))<=20:
					try:
						pvalue=bartlett(plotData[x],plotData[y])[1]		
					except:
						pvalue="NA"
						#pvalue=1.0
	
					if minuslog10pvalue and str(pvalue)!="NA":
						try:
							pvalue=-1*log(pvalue,10)
						except:
							pvalue=-1000.0
	
	
					print >> stdout,pvalue,
					pvalueRow.append(pvalue)
					#else:
					#	print >>  stdout,wilcoxon(plotData[x],plotData[y])[1], # this is two-tailed already stdout, "", #
			print >> stdout,"";	
		
		if plotPvalueCluster:
			makePValueRawPlot(outputClusterPrefix+"_bartlett_raw",xtickLabels,pvalueM)
			makePValueClusterPlot(outputClusterPrefix+"_bartlett",xtickLabels,pvalueM,methodCluster)	
		
		
		#####

	figure(figsize=figsz)
	subplots_adjust(top=0.9, bottom=botta, left=0.2, right=0.8)
	
	if len(titl)==0:
		titl=outputFile


	plotExpBox(plotData,xtickLabels,showIndPoints,mark,markMean,showMean,notch,whisker,outliers,xlegendrotation,xlabe,ylabe,titl,showSampleSizes,showViolin,showBox,annot,trendData,showLegend,makePzfxFile,makeBinMatrix,dividePlots)
	
	#ylim([0,200])
	for m in medianToDraw:
		axhline(y=m,linestyle=':',color='gray')

	savefig(outputFile,bbox_inches="tight")

	if len(plotHistogramToFile)>0:
		drawHistogram(plotHistogramToFile,plotData,xtickLabels)
		drawDensigram(plotHistogramToFile+".density.png",plotData,xtickLabels)

def mulArray(x,n):
	L=[]
	for i in range(0,n):
		L.append(x)

	return L

def usageExit(programName):
	print >> stderr,programName,"outputFile [ inputFile1 valCol1 inputFile2 valCol2 ...] "
	print >> stderr,"Options:"
	print >> stderr,"-t -F -d --fs seperator"
	print >> stderr,"-r --headerRow headerRow"
	print >> stderr,"-s --startRow startRow"
	print >> stderr,"-p --showIndPoints"
	print >> stderr,"-m --showMean"
	print >> stderr,"-n --notch"
	print >> stderr,"--first-col-annot first column of each valCol is annotation"
	print >> stderr,"--plot-trend draw trend curves per file"	
	print >> stderr,"--xtick-rotation degree"
	print >> stderr,"--offWhisker"
	print >> stderr,"--offOutliers"
	print >> stderr,"--hide-violin"
	print >> stderr,"--minus-log10-pvalue output pvalue as -log10(pvalue)"
	print >> stderr,"--pvalue-cluster-as prefix  make pvalue cluster heatmap using 1-pvalue as distance metric"
	print >> stderr,"--pvalue-cluster-method method   cluster using one of the following method for the pvalue cluster heatmap"
	print >> stderr,"--vfacecolor r,g,b,a --valpha a facecolor and alpha for violin plots"
	print >> stderr,"--xlabel label"
	print >> stderr,"--ylabel label"
	print >> stderr,"--figsize w,h"
	print >> stderr,"--title title (default is filename)"
	print >> stderr,"--show-sample-sizes"
	print >> stderr,"--relabel-as label1,label2,label3,...  relabel the columns"
	print >> stderr,"--plot-hist filename"
	print >> stderr,"--plot-median-for-group cols"
	print >> stderr,"--log base"
	print >> stderr,"--show-legend"
	print >> stderr,"--out-pzfx intemplate,outfile"
	print >> stderr,"--out-bin-matrix outfile,numbins"
	print >> stderr,"--write-data-summary-stat outfile write to outfile a table of mean and stddev etc"
	print >> stderr,"--data-summary-stat-range min,max only consider data within the range min and max for doing summary stat table. Use NA to say no bound for each of the bounds"
	print >> stderr,"--min-num-data-to-keep. set the minimal number of datapoints per col to keep. [2]"
	print >> stderr,"--outXYZPvalues prefix. Write pvalues for statistics in the form of xyz format"
	print >> stderr,"--ylims miny,maxy set min and max y to plot"
	print >> stderr,"--whisker-style linestyle. set whisker line style, e.g., - for solid line"
	print >> stderr,"--axhline y,linestyle,color draw horizontal line"
	print >> stderr,"--skip-stat"
	print >> stderr,"--divide-plots t1,t2,..  divide plots into subpopulations per column by thresholds t1,t2,...."
	print >> stderr, "from PyCluster (see http://www.biopython.org/DIST/docs/api/Bio.Cluster.Record-class.html#treecluster)"
	print >> stderr, "method   : specifies which linkage method is used:"
	print >> stderr, "           method=='s': Single pairwise linkage"
	print >> stderr, "           method=='m': Complete (maximum) pairwise linkage (default)"
	print >> stderr, "           method=='c': Centroid linkage"
	print >> stderr, "           method=='a': Average pairwise linkage"
	
	explainColumns(stderr)

	sys.exit()

if __name__=='__main__':
	programName=argv[0]
	optlist,args=getopt(argv[1:],'t:F:d:r:s:pmn',['fs=','headerRow=','startRow=','showIndPoints','showMean','notch','offWhisker','offOutliers','pvalue-cluster-as=','pvalue-cluster-method=','xtick-rotation=','xlabel=','ylabel=','figsize=','title=','show-sample-sizes','trim-to-min-size','relabel-as=','plot-hist=','plot-median-for-group=','log=','bottom=','hide-violin','hide-box','plot-trend','first-col-annot','show-legend','out-pzfx=','pzfx-tableref-id=','out-bin-matrix=','write-data-summary-stat=','data-summary-stat-range=','minus-log10-pvalue','min-num-data-to-keep=','valpha=','vfacecolor=',"outXYZPvalues=",'ylims=','whisker-style=','axhline=','skip-stat','divide-plots='])

	headerRow=1
	startRow=2
	fs="\t"
	showIndPoints=False
	showMean=False
	whisker=True
	outliers=True
	notch=0
	logb=0
	plotHistogramToFile=""
	plotMedianForGroups=[]
	xlegendrotation=0
	makePvalueClusters=False
	pvalueClusterOutputPrefix=""
	pvalueClusterMethod="a"
	xlabe="Samples"
	ylabe="Values"
	titl=""
	figsz=(8,6)
	showSampleSizes=False
	botta=0.3
	filenames=[]
	valcols=[]
	headers=[]
	relabels=[]
	firstColAnnot=False
	plotTrend=False
	trimToMinSize=False
	showViolin=True
	showBox=True
	showLegend=False
	makePzfxFile=None
	makeBinMatrix=None
	pzfxTableRefID="Table0"
	#if len(args)!=3:
	writeDataSummaryStat=""
	summaryStatRange=[None,None]
	minuslog10pvalue=False
	minNDataToKeep=2
	vfacecolor='y'
	valpha=1.0 #0.3
	outXYZPvalues=None
	ylims=None
	axhlines=[]
	whiskerStyle="--"
	skipStat=False
	dividePlots=[]
	
	#else:
	try:
		outputFile=args[0]

	
		for a,v in optlist:
			if a in ["-F","-t","-d","--fs"]:
				fs=replaceSpecialChar(v)
			elif a in ["-s","--startRow"]:
				startRow=int(v)
			elif a in ["-r","--headerRow"]:
				headerRow=int(v)
			elif a in ["-p","--showIndPoints"]:
				showIndPoints=True
			elif a in ["-m","--showMean"]:
				showMean=True
			elif a in ["-n","--notch"]:
				notch=1
			elif a in ["--offOutliers"]:
				outliers=False
			elif a in ["--offWhisker"]:
				whisker=False
			elif a in ["--pvalue-cluster-as"]:
				makePvalueClusters=True
				pvalueClusterOutputPrefix=v
			elif a in ["--pvalue-cluster-method"]:
				pvalueClusterMethod=v
			elif a in ["--xtick-rotation"]:
				xlegendrotation=int(v)
			elif a in ["--xlabel"]:
				xlabe=v
			elif a in ["--ylabel"]:
				ylabe=v
			elif a in ["--figsize"]:
				v=v.split(",")
				figsz=(int(v[0]),int(v[1]))
			elif a in ["--title"]:
				titl=v
			elif a in ["--show-sample-sizes"]:
				showSampleSizes=True
			elif a in ["--trim-to-min-size"]:
				trimToMinSize=True
			elif a in ["--relabel-as"]:
				print >> stderr,"v=",v
				relabels=v.split(",")
			elif a in ['--log']:
				logb=log(float(v))
			elif a in ['--plot-hist']:
				plotHistogramToFile=v
			elif a in ['--plot-median-for-group']:
				plotMedianForGroups.append(v)
			elif a in ['--bottom']:
				botta=float(v)
			elif a in ['--hide-violin']:
				showViolin=False
			elif a in ['--hide-box']:
				showBox=False
			elif a in ['--first-col-annot']:
				firstColAnnot=True
			elif a in ['--plot-trend']:
				plotTrend=True
			elif a in ['--show-legend']:
				showLegend=True
			elif a in ['--out-pzfx']:
				makePzfxFile=v.split(",")
			elif a in ['--out-bin-matrix']:
				makeBinMatrix=v.split(",")
				#print >> stderr,makeBinMatrix
				makeBinMatrix[1]=int(makeBinMatrix[1])
			elif a in ['--min-num-data-to-keep']:
				minNDataToKeep=int(v)
			elif a in ['--data-summary-stat-range']:
				mi,ma=v.split(",")
				summaryStatRange=[]
				try:
					mi=float(mi)
					summaryStatRange.append(mi)
				except:
					summaryStatRange.append(None)
				try:
					ma=float(ma)
					summaryStatRange.append(ma)
				except:
					summaryStatRange.append(None)
				
			elif a in ['--write-data-summary-stat']:
				writeDataSummaryStat=v
			elif a in ['--minus-log10-pvalue']:
				minuslog10pvalue=True
			elif a in ['--valpha']:
				valapha=float(v)
			elif a in ['--vfacecolor']:
				vrgba=v.split(",")
				if len(vrgba)<3:
					vfacecolor=v
				else:
					vfacecolor=[]
					for vr in vrgba:
						vfacecolor.append(float(vr))
					valpha=vfacecolor[3]
			elif a in ['--outXYZPvalues']:
				outXYZPvalues=v
			elif a in ['--ylims']:
				
				
				yl=v.split(",")
				ylims=[float(yl[0]),float(yl[1])]
			elif a in ['--whisker-style']:
				whiskerStyle=v
			elif a in ['--axhline']:
				v=v.split(",")
				axhlines.append(v) #[float(v[0]),v[1],v[2]])
			elif a in ['--skip-stat']:
				skipStat=True
			elif a in ['--divide-plots']:
				dividePlots=[float(x) for x in v.split(",")]
	except:
		traceback.print_stack()
		usageExit(programName)
	
	#print >> stderr,args
	for i in range(1,len(args),2):
		thisFilenames=glob(args[i])
		valcolstring=args[i+1]
		filenames.extend(thisFilenames)
		for filenam in thisFilenames:
			header,prestarts=getHeader(filenam,headerRow,startRow,fs)
			cols=getCol0ListFromCol1ListStringAdv(header,valcolstring)
			print >> stderr, thisFilenames, cols
			valcols.append(cols)
			headers.append(header)	
	
	if makePvalueClusters:
		from Bio.Cluster.cluster import *
		from Bio.Cluster import *
	
	
	if showLegend:
		figsz=(figsz[0]*2,figsz[1])
	
	
	if makePzfxFile:
		makePzfxFile+=[pzfxTableRefID]
	
	plotExpBox_Main(filenames,headers,valcols,outputFile,fs,startRow,showIndPoints,'bo','g--',showMean,notch,whisker,outliers,makePvalueClusters,pvalueClusterOutputPrefix,pvalueClusterMethod,xlegendrotation,xlabe,ylabe,figsz,titl,showSampleSizes,trimToMinSize,relabels,logb,plotHistogramToFile,plotMedianForGroups,botta,showViolin,showBox,firstColAnnot,plotTrend,showLegend,makePzfxFile,makeBinMatrix,writeDataSummaryStat,summaryStatRange,minuslog10pvalue,minNDataToKeep,vfacecolor,valpha,outXYZPvalues,dividePlots)	
		
		
