#!/usr/bin/env python

from pylab import *
from albertcommon import *
from sys import *
from getopt import getopt
from os import system
'''
NUM_COLORS = 22

cm = get_cmap('gist_rainbow')
for i in range(NUM_COLORS):
    color = cm(1.*i/NUM_COLORS)  # color will now be an RGBA tuple

# or if you really want a generator:
cgen = (cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS))
'''

def printUsageAndExit(programName):
	print >> stderr,programName,"[options] outName"
	print >> stderr,"[--legendOut filenameL] [--fs t=tab] [--headerRow x=1] [--startRow y=2] [--xcol x=2] [--ycol y=3] [--labelcol L=1] [--config configfile]  --file filename. Plot filename data with "
	print >> stderr,"\t--fs t. set field separator"
	print >> stderr,"\t--headerRow x. set header row"
	print >> stderr,"\t--startRow y. set data start row"
	print >> stderr,"\t--xcol xcol"
	print >> stderr,"\t--ycol ycol"
	print >> stderr,"\t--XLabel xlabel"
	print >> stderr,"\t--YLabel	ylabel"	
	print >> stderr,"\t--config configfile. load config file"
	print >> stderr,"\t--suppress-NA-error. Don't quit on NA error"
	exit(1)

startRow=2
headerRow=1
fs="\t"
xcol=2
ycol=3
labelcol=1
configfile=None
filename=None
legendFile=None
suppressNAError=False
argsattrMatrix=dict()
xlabe=""
ylabe=""

def reinitLoadingParams():
	global startRow,headerRow,fs,xcol,ycol,labelcol,configfile,filename
	startRow=2
	headerRow=1
	fs="\t"
	xcol="2"
	ycol="3"
	labelcol="1"
	configfile=None
	filename=None
	legendFile=None
	suppressNAError=False
	#argsattrMatrix=dict()
	
def toFloatArray(L):
	F=[]
	for s in L:
		F.append(float(s))
	return F
	

	
	
	
def plotData(filename,attrMatrix,startRow,labelcol,xcol,ycol,fs,legendOut,suppressNAError,onlyPlotGroup):
	# !groupDivider	.
	# !groupNameComponent	1-_1
	# !hasGroup	no
	# MATRIX ATTR rgbColor r,g,b
	# MATRIX ATTR colorMapColor colorMapName:indx[0.0-1.0]
	hasGroup=(getAttrWithDefaultValue(attrMatrix,"!hasGroup","no").lower()=="yes")
	centerPlot=(getAttrWithDefaultValue(attrMatrix,"!centerPlot","no").lower()=="yes")
	squarePlot=(getAttrWithDefaultValue(attrMatrix,"!squarePlot","no").lower()=="yes")
	hideDots=(getAttrWithDefaultValue(attrMatrix,"!hideDots","no").lower()=="yes")
	dottedLineThruCenter=(getAttrWithDefaultValue(attrMatrix,"!dottedLineThruCenter","no").lower()=="yes")
	groupDivider=getAttrWithDefaultValue(attrMatrix,"!groupDivider",".")
	groupNameComponent=getAttrWithDefaultValue(attrMatrix,"!groupNameComponent","1")
	defaultColor=toFloatArray(getAttrWithDefaultValue(attrMatrix,"!color",(0.0,0.0,0.0,1.0)))
	defaultMarkerStyle=getAttrWithDefaultValue(attrMatrix,"!markerStyle",".")
	defaultLineWidth=float(getAttrWithDefaultValue(attrMatrix,"!lineWidth",1))
	defaultMarkerSize=float(getAttrWithDefaultValue(attrMatrix,"!markerSize",1))
	defaultShowLabel=getAttrWithDefaultValue(attrMatrix,"!showLabel","no").lower()
	XLabel=getAttrWithDefaultValue(attrMatrix,"!XLabel",xlabe)
	YLabel=getAttrWithDefaultValue(attrMatrix,"!YLabel",ylabe)
	groupOrder=getAttrWithDefaultValue(attrMatrix,"!groupOrder",None)
	plotSlopedLines=getAttrWithDefaultValue(attrMatrix,"!plotSlopedLines","").strip()
	xlimsSet=getAttrWithDefaultValue(attrMatrix,"!xlims","").strip()
	ylimsSet=getAttrWithDefaultValue(attrMatrix,"!ylims","").strip()
	smartGroups=getAttrWithDefaultValue(attrMatrix,"!smartGroups","")
	defaultShowSmartLabel=getAttrWithDefaultValue(attrMatrix,"!showSmartLabel",None)
	labelOffsetX=float(getAttrWithDefaultValue(attrMatrix,"!labelOffsetX","0"))
	labelOffsetY=float(getAttrWithDefaultValue(attrMatrix,"!labelOffsetY","0"))
	smlabelOffsetX=getAttrWithDefaultValue(attrMatrix,"!smlabelOffsetX","0")
	smlabelOffsetY=getAttrWithDefaultValue(attrMatrix,"!smlabelOffsetY","0")
	showLabelArrow=(getAttrWithDefaultValue(attrMatrix,"!showLabelArrow","no").lower()=="yes")
	
	if len(smartGroups)>0:
		smartGroups=smartGroups.split(";")
		for i in range(0,len(smartGroups)):
			smartGroupStr=smartGroups[i]
			smartGroups[i]=smartGroupStr.split(":")
			
	else:
		smartGroups=None
	
	
	#print >> stderr,"attrMatrix",attrMatrix
	#print >> stderr,"plotSlopedLines",plotSlopedLines
	if len(plotSlopedLines)>0:
		plotSlopedLines=plotSlopedLines.split(";")
		for i in range(0,len(plotSlopedLines)):
			m,c,s=plotSlopedLines[i].split(",")
			plotSlopedLines[i]=(float(m),float(c),s)
		
		#print >> stderr,plotSlopedLines	
	else:
		plotSlopedLines=[]
		
	X=[]
	Y=[]
	labels=[]
	groups=dict()
	maxX=None
	minX=None
	maxY=None
	minY=None
	
	#print >> stderr,"startRow=",startRow
	
	fil=open(filename)
	lino=0
	for lin in fil:
		lin=lin.rstrip("\r\n")
		lino+=1
		
		fields=lin.split(fs)
		
		if lino<startRow:
			if lino==startRow-1:
				#print >> stderr,"XLabel=",XLabel
				if XLabel.strip()=="__useHeader__":
					XLabel=fields[xcol]
				if YLabel.strip()=="__useHeader__":
					YLabel=fields[ycol]
			continue
		
		
		try:
			x=float(fields[xcol])
			y=float(fields[ycol])
			if maxX==None:
				maxX=x
			if minX==None:
				minX=x
			if maxY==None:
				maxY=y
			if minY==None:
				minY=y
			minX=min(minX,x)
			maxX=max(maxX,x)
			minY=min(minY,y)
			maxY=max(maxY,y)
			
		except ValueError:
			if not suppressNAError:
				print >> stderr,"value error for converting to float x=",fields[xcol],"y=",fields[ycol]
				exit(1)
			continue
		
		label=fields[labelcol]
		labels.append(label)

		X.append(x)
		Y.append(y)
		
		if smartGroups:
			for groupName,groupLogic in smartGroups:
				#print >> stderr,groupName,groupLogic
				if eval(groupLogic):
					try:
						groupLabels,groupX,groupY=groups[groupName]
					except KeyError:
						groupLabels=[]
						groupX=[]
						groupY=[]
						groups[groupName]=(groupLabels,groupX,groupY)
					
					groupLabels.append(groupName) ##label??
					groupX.append(x)
					groupY.append(y)
					#exlusive group?? if yes, break
			
		if hasGroup:
			#which group is this label?
			labelon=label.split(groupDivider)
			
			groupName=groupDivider.join(getSubvector(labelon,getCol0ListFromCol1ListStringAdv(labelon,groupNameComponent)))
			#print >> stderr,labelon,groupNameComponent,groupNamey
			try:
				groupLabels,groupX,groupY=groups[groupName]
			except KeyError:
				
				groupLabels=[]
				groupX=[]
				groupY=[]
				groups[groupName]=(groupLabels,groupX,groupY)
			
			groupLabels.append(label)
			groupX.append(x)
			groupY.append(y)
		
					
	fil.close()
	
	#now plot
	if not hasGroup and not smartGroups:
		groups["___default___"]=(labels,X,Y)
	
	if legendOut:
		legendOutDataStream=open(legendOut+".legendData","w+") #need headear??
	
	if groupOrder:
		groupOrdered=groupOrder.split("|")
	else:
		groupOrdered=groups.keys()
	
	for groupName in groupOrdered:
		try:
			groupData=groups[groupName]
			#print >> stderr,"plotting",groupName,groupData
		except KeyError:
			continue
		
		if len(onlyPlotGroup)>0 and groupName not in onlyPlotGroup:
			#print >> stderr,groupName
			continue
			
		groupLabels,groupX,groupY=groupData
		markerStyle=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"markerStyle",defaultMarkerStyle)
		
		#for color, either rgbcolor or colormapcolor:
		rgbacolor=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"RGBAColor",None)
		colormapcolor=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"colorMapColor",None)
		#if colormapcolor==None:
		#	print >> stderr,"n:",groupName,attrMatrix
		lineWidth=float(getLevel2AttrWithDefaultValue(attrMatrix,groupName,"lineWidth",defaultLineWidth))
		markerSize=float(getLevel2AttrWithDefaultValue(attrMatrix,groupName,"markerSize",defaultMarkerSize))
		showLabel=(getLevel2AttrWithDefaultValue(attrMatrix,groupName,"showLabel",defaultShowLabel).lower()=="yes")
		markerEdgeColor=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"markerEdgeColor","0,0,0,0")
		showSmartLabel=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"showSmartLabel",defaultShowSmartLabel)
		showReLabelAs=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"showReLabelAs",None)
		
		#print >> stderr,"showSmartLabel=",showSmartLabel
		
		if rgbacolor:
			_r,_g,_b,_a=toFloatArray(rgbacolor.split(","))
		elif colormapcolor:
			colormapName,idx=colormapcolor.split(":")
			_r,_g,_b,_a=get_cmap(colormapName)(float(idx))
		else:
			_r,_g,_b,_a=defaultColor
		
		
		markerEdgeColor=toFloatArray(markerEdgeColor.split(","))
		
		if not hideDots:
			plot(groupX,groupY,markerStyle,color=(_r,_g,_b),alpha=_a,markeredgecolor=markerEdgeColor,markeredgewidth=lineWidth,linewidth=lineWidth,markersize=markerSize)
			
		
		if XLabel:
			xlabel(XLabel)
		
		if YLabel:
			ylabel(YLabel)
			
		
		if showLabel:
			for label,x,y in zip(groupLabels,groupX,groupY):
				text(x+labelOffsetX+eval(smlabelOffsetX),y+labelOffsetY+eval(smlabelOffsetY),label,horizontalalignment="center",verticalalignment="center")
		elif showReLabelAs:
			for x,y in zip(groupX,groupY):
				text(x+labelOffsetX+eval(smlabelOffsetX),y+labelOffsetY+eval(smlabelOffsetY),showReLabelAs,horizontalalignment="center",verticalalignment="center")
		elif showSmartLabel:
			for label,x,y in zip(groupLabels,groupX,groupY):
				LABELCOMPS=label.split(groupDivider)
				GROUPNAME=groupName
				LABEL=label
				X=x
				Y=y
				#print >> stderr,eval(showSmartLabel)
				text(x+labelOffsetX+eval(smlabelOffsetX),y+labelOffsetY+eval(smlabelOffsetY),eval(showSmartLabel),horizontalalignment="center",verticalalignment="center")
		
		if legendOut:	
			print >> legendOutDataStream,groupName+"\t"+str(_r)+"\t"+str(_g)+"\t"+str(_b)+"\t"+str(_a)
			
	
	if len(xlimsSet)>0:
		#print >> stderr,xlimsSet
		cxmin,cxmax=xlimsSet.split(",")
		xlim(float(cxmin),float(cxmax))
	
	if len(ylimsSet)>0:	
		cymin,cymax=ylimsSet.split(",")
		ylim(float(cymin),float(cymax))
	
	if centerPlot:
		if minX*maxX<0:
			#opposite sign
			maxAbsX=max(fabs(minX),maxX)*1.25
			xlim(-maxAbsX,maxAbsX)
		
		if minY*maxY<0:
			maxAbsY=max(fabs(minY),maxY)*1.25
			ylim(-maxAbsY,maxAbsY)
		
	if squarePlot:
		cxmin,cxmax=xlim()
		cymin,cymax=ylim()
		
		xlength=cxmax-cxmin
		ylength=cymax-cymin
		
		setlength=max(xlength,ylength)
		
		cxmin-=(setlength-xlength)/2
		cxmax+=(setlength-xlength)/2
		cymin-=(setlength-ylength)/2
		cymax+=(setlength-ylength)/2
		
		xlim(cxmin,cxmax)
		ylim(cymin,cymax)
		
	
	
	if dottedLineThruCenter:
		cxmin,cxmax=xlim()
		cymin,cymax=ylim()
		
		axhline(linestyle=':',y=(cymax+cymin)/2.0)
		axvline(linestyle=':',x=(cxmax+cxmin)/2.0)
		
	if len(plotSlopedLines)>0:
		cxmin,cxmax=xlim()
		cymin,cymax=ylim()
		
		#minmin=min(cxmin,cymin)
		#maxmax=max(cxmax,cymax)
		
		for m,c,s in plotSlopedLines:
			#print >> stderr,"plot sloped line",[cxmin,cxmin*m+c],[cxmax,cxmax*m+c]
			plot([cxmin,cxmax],[cxmin*m+c,cxmax*m+c],s)
		
		xlim(cxmin,cxmax)
		ylim(cymin,cymax)
	
	if legendOut:
		legendOutDataStream.close()
		
def SVGText(stream,x,y,text,fontFamily,fontSize):
	print >> stream,"<text x=\""+str(x)+"\" y=\""+str(y)+"\" font-family=\""+fontFamily+"\" font-size=\""+str(fontSize)+"\">"+text+"</text>"
				
if __name__=='__main__':
	programName=argv[0]
	if len(argv[1:])<1:
		printUsageAndExit(programName)
	
	
	reinitLoadingParams()
	
	legendDataStreamsCreated=set()
	
	opts,args=getopt(argv[1:],'',['fs=','headerRow=','startRow=','xcol=','ycol=','labelcol=','config=','file=',"legendOut=",'suppress-NA-error','XLabel=','YLabel=','onlyPlotGroup=','title='])

	fileParamsPassed=False
	onlyPlotGroup=[]
	
	titleText=""

	try:
		outName,=args
	except:
		printUsageAndExit(programName)
	
	for o,v in opts:
		if fileParamsPassed==True and o!="--file":
			print >> stderr,"Warning, --file should be at the end of all optional args to take the optional args in effect abort."
			exit(1)
		if o=='--fs':
			fs=v
		elif o=='--headerRow':
			headerRow=int(v)
		elif o=='--startRow':
			startRow=int(v)
		elif o=='--xcol':
			xcol=v
		elif o=='--ycol':
			ycol=v
		elif o=='--labelcol':
			labelcol=v
		elif o=='--config':
			configfile=v
		elif o=='--legendOut':
			legendFile=v
		elif o=='--suppress-NA-error':
			suppressNAError=True
		elif o=='--XLabel':
			xlabe=v
		elif o=='--YLabel':
			ylabe=v
		elif o=='--file':
			fileParamsPassed=True
			filename=v
			header,prestarts=getHeader(filename,headerRow,startRow,fs)	
			labelcol=getCol0ListFromCol1ListStringAdv(header,labelcol)[0]
			xcol=getCol0ListFromCol1ListStringAdv(header,xcol)[0]
			ycol=getCol0ListFromCol1ListStringAdv(header,ycol)[0]
	
			
			if configfile:
				attrMatrix=readNamedAttrMatrix(configfile)
			else:
				attrMatrix=dict()
			
			for ke,va in argsattrMatrix.items():
				attrMatrix[ke]=va
			
			
			if legendFile:
				if legendFile not in legendDataStreamsCreated:
					fil=open(legendFile+".legendData","w")
					fil.close()
					legendDataStreamsCreated.add(legendFile)
				
			plotData(filename,attrMatrix,startRow,labelcol,xcol,ycol,fs,legendFile,suppressNAError,onlyPlotGroup)
			
			
			
			#after everything
			reinitLoadingParams()
		elif o=='--onlyPlotGroup':
			onlyPlotGroup.append(v)
		elif o=='--title':
			titleText=v
		else:
			key=o[2:]
			argsattrMatrix["!"+key]=v		
	if titleText!="":
		title(titleText)	
	savefig(outName)
	
	for legendFileI in legendDataStreamsCreated:
		legendDataStreamF=open(legendFileI+".legendData")
		legendF=open(legendFileI+"_legend.svg","w")
		legendF2=open(legendFileI+"_legend00.svg","w")
		
		cury=0
		print >> legendF, "<?xml version=\"1.0\" standalone=\"no\"?>"
		print >> legendF, "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\""
		print >> legendF, "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"
		print >> legendF, "<svg width=\"100%\" height=\"100%\" version=\"1.1\""
		print >> legendF, "xmlns=\"http://www.w3.org/2000/svg\">"

		print >> legendF2, "<?xml version=\"1.0\" standalone=\"no\"?>"
		print >> legendF2, "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\""
		print >> legendF2, "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"
		print >> legendF2, "<svg width=\"100%\" height=\"100%\" version=\"1.1\""
		print >> legendF2, "xmlns=\"http://www.w3.org/2000/svg\">"
			
		for lin in legendDataStreamF:
			if len(lin)<1:
				continue
			
			lin=lin.rstrip("\r\n")
			
			groupName,r,g,b,a=lin.split("\t")
			r=int(round(float(r)*255))
			g=int(round(float(g)*255))
			b=int(round(float(b)*255))
			
			
			showReLabelAs=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"showReLabelAs",None)
			if showReLabelAs:
				groupName+="("+showReLabelAs+")"
			
			print >> legendF,"<rect x=\""+str(10)+"\" y=\""+str(cury)+"\" width=\"20\" height=\"20\" stroke=\"black\" stroke-width=\"1\" style=\"fill:rgba("+str(r)+","+str(g)+","+str(b)+","+str(a)+");\"/>"
			print >> legendF2,"<rect x=\""+str(10)+"\" y=\""+str(cury)+"\" width=\"20\" height=\"20\" stroke=\"black\" stroke-width=\"1\" style=\"fill:rgba("+str(r)+","+str(g)+","+str(b)+","+str(a)+");\"/>"
			SVGText(legendF,30+5,cury+18,groupName,"Arial",20)
			SVGText(legendF2,30+5,cury,groupName,"Arial",20)
			cury+=30
		
		
		print >> legendF, "</svg>"
		print >> legendF2, "</svg>"
		legendF.close()
		legendF2.close()
		legendDataStreamF.close()
		
		system("convert "+legendFileI+"_legend00.svg "+legendFileI+"_legend.png")
		system("rm "+legendFileI+"_legend00.svg ")