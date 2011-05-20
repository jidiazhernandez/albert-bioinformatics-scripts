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
	print >> stderr,"\t--config configfile. load config file"
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
	
	
def toFloatArray(L):
	F=[]
	for s in L:
		F.append(float(s))
	return F
	
def plotData(filename,attrMatrix,startRow,labelcol,xcol,ycol,fs,legendOut):
	# !groupDivider	.
	# !groupNameComponent	1-_1
	# !hasGroup	no
	# MATRIX ATTR rgbColor r,g,b
	# MATRIX ATTR colorMapColor colorMapName:indx[0.0-1.0]
	hasGroup=(getAttrWithDefaultValue(attrMatrix,"!hasGroup","no").lower()=="yes")
	groupDivider=getAttrWithDefaultValue(attrMatrix,"!groupDivider",".")
	groupNameComponent=getAttrWithDefaultValue(attrMatrix,"!groupNameComponent","1")
	defaultColor=toFloatArray(getAttrWithDefaultValue(attrMatrix,"!color",(0.0,0.0,0.0,1.0)))
	defaultMarkerStyle=getAttrWithDefaultValue(attrMatrix,"!markerStyle","o")
	defaultLineWidth=float(getAttrWithDefaultValue(attrMatrix,"!lineWidth",1))
	defaultMarkerSize=float(getAttrWithDefaultValue(attrMatrix,"!markerSize",1))
	defaultShowLabel=getAttrWithDefaultValue(attrMatrix,"!showLabel","no").lower()
	groupOrder=getAttrWithDefaultValue(attrMatrix,"!groupOrder",None)
	
	X=[]
	Y=[]
	labels=[]
	groups=dict()
	
	fil=open(filename)
	lino=0
	for lin in fil:
		lin=lin.rstrip("\r\n")
		lino+=1
		if lino<startRow:
			continue
		fields=lin.split(fs)
		label=fields[labelcol]
		labels.append(label)
		x=float(fields[xcol])
		y=float(fields[ycol])
		X.append(x)
		Y.append(y)
		if hasGroup:
			#which group is this label?
			labelon=label.split(groupDivider)
			groupName=groupDivider.join(getSubvector(labelon,getCol0ListFromCol1ListStringAdv(labelon,groupNameComponent)))
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
	if not hasGroup:
		groups["___default___"]=(labels,x,y)
	
	if legendOut:
		legendOutDataStream=open(legendOut+".legendData","w+") #need headear??
	
	if groupOrder:
		groupOrdered=groupOrder.split("|")
	else:
		groupOrdered=groups.keys()
	
	for groupName in groupOrdered:
		try:
			groupData=groups[groupName]
		except KeyError:
			continue
			
		groupLabels,groupX,groupY=groupData
		markerStyle=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"markerStyle",defaultMarkerStyle)
		
		#for color, either rgbcolor or colormapcolor:
		rgbacolor=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"RGBAColor",None)
		colormapcolor=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"colorMapColor",None)
		lineWidth=float(getLevel2AttrWithDefaultValue(attrMatrix,groupName,"lineWidth",defaultLineWidth))
		markerSize=float(getLevel2AttrWithDefaultValue(attrMatrix,groupName,"markerSize",defaultMarkerSize))
		showLabel=(getLevel2AttrWithDefaultValue(attrMatrix,groupName,"showLabel",defaultShowLabel).lower()=="yes")
		showReLabelAs=getLevel2AttrWithDefaultValue(attrMatrix,groupName,"showReLabelAs",None)
		if rgbacolor:
			_r,_g,_b,_a=toFloatArray(rgbacolor.split(","))
		elif colormapcolor:
			colormapName,idx=colormapcolor.split(":")
			_r,_g,_b,_a=get_cmap(colormapName)(float(idx))
		else:
			_r,_g,_b,_a=defaultColor
		
		plot(groupX,groupY,markerStyle,color=(_r,_g,_b),alpha=_a,linewidth=lineWidth,markersize=markerSize)
		
		if showLabel:
			for label,x,y in zip(groupLabels,groupX,groupY):
				text(x,y,label)
		elif showReLabelAs:
			for x,y in zip(groupX,groupY):
				text(x,y,showReLabelAs)
		
		if legendOut:	
			print >> legendOutDataStream,groupName+"\t"+str(_r)+"\t"+str(_g)+"\t"+str(_b)+"\t"+str(_a)
	
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
	
	opts,args=getopt(argv[1:],'',['fs=','headerRow=','startRow=','xcol=','ycol=','labelcol=','config=','file=',"legendOut="])

	try:
		outName,=args
	except:
		printUsageAndExit(programName)
	
	for o,v in opts:
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
		elif o=='--file':
			filename=v
			header,prestarts=getHeader(filename,headerRow,startRow,fs)	
			labelcol=getCol0ListFromCol1ListStringAdv(header,labelcol)[0]
			xcol=getCol0ListFromCol1ListStringAdv(header,xcol)[0]
			ycol=getCol0ListFromCol1ListStringAdv(header,ycol)[0]
			
			if configfile:
				attrMatrix=readNamedAttrMatrix(configfile)
			else:
				attrMatrix=dict()
			
			if legendFile:
				if legendFile not in legendDataStreamsCreated:
					fil=open(legendFile+".legendData","w")
					fil.close()
					legendDataStreamsCreated.add(legendFile)
				
			plotData(filename,attrMatrix,startRow,labelcol,xcol,ycol,fs,legendFile)
			
			
			
			#after everything
			reinitLoadingParams()
			
		
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