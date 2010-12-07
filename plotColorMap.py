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

from optparse import OptionParser
from albertcommon import *
from sys import *
import numpy as np
import matplotlib.pyplot as plt
from pylab import *


def showAvailableColorMapToFigure(figFileName):
	a = np.linspace(0, 1, 256).reshape(1,-1)
	a = np.vstack((a,a))
	
	# Get a list of the colormaps in matplotlib.  Ignore the ones that end with
	# '_r' because these are simply reversed versions of ones that don't end
	# with '_r'
	maps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
	nmaps = len(maps) + 1
	
	fig = plt.figure(figsize=(5,10))
	fig.subplots_adjust(top=0.99, bottom=0.01, left=0.2, right=0.99)
	for i,m in enumerate(maps):
	    ax = plt.subplot(nmaps, 1, i+1)
	    plt.axis("off")
	    plt.imshow(a, aspect='auto', cmap=plt.get_cmap(m), origin='lower')
	    pos = list(ax.get_position().bounds)
	    fig.text(pos[0] - 0.01, pos[1], m, fontsize=10, horizontalalignment='right')
	
	savefig(figFileName)

def toFloatListWithNAMask(L):
	fL=[]
	Mask=[] #1 or 0:NA
	vmin=None
	vmax=None
	for x in L:
		try:
			fvalue=float(x)
		except:
			fL.append(-100000.00)
			Mask.append(0)
			continue
			
		fL.append(fvalue)	
		Mask.append(1)
		if vmin==None:
			vmin=fvalue
			vmax=fvalue
		else:
			vmin=min(vmin,fvalue)
			vmax=max(vmax,fvalue)
		
	return (fL,Mask,vmin,vmax)

def plotColorMatrix(infile,figFileName,options):
	#load file
	fil=open(infile)
	lino=0
	
	rownames=[]
	
	values=[]
	masks=[]
	
	minval=None
	maxval=None
	
	
	for lin in fil:
		fields=lin.rstrip("\r\n").split(options.fs)
		lino+=1
		if lino==1:
			colnames=fields[1:]
		else:
			rownames.append(fields[0])
			rowvalues,rowmask,rowmin,rowmax=toFloatListWithNAMask(fields[1:])
			if rowmin!=None:
				if minval==None:
					minval=rowmin
					maxval=rowmax
				else:
					minval=min(rowmin,minval)
					maxval=max(rowmax,maxval)
			
			values.append(rowvalues)
			masks.append(rowmask)
			
	fil.close()
	
	#print >> stderr,masks
	masks.reverse()
	#print >> stderr,masks
	values.reverse()
	#print >> stderr,values
	rownames.reverse()
	
	#now draw
	if options.dataRange:
		vminToDraw=float(options.dataRange[0])
		vmaxToDraw=float(options.dataRange[1])
	else:
		vminToDraw=minval
		vmaxToDraw=maxval
	
	
	
	im=matshow(array(values),cmap=plt.get_cmap(options.colormapName),vmin=vminToDraw,vmax=vmaxToDraw)
	



	for label in im.axes.xaxis.get_ticklabels():
		label.set_rotation(options.xtickRotation)

	for tick in im.axes.xaxis.get_major_ticks():
		tick.tick1On=False
		tick.tick2On=False
		
	for tick in im.axes.yaxis.get_major_ticks():
		tick.tick1On=False
		tick.tick2On=False
		
	ncols=len(colnames)
	nrows=len(rownames)
	

	
	#now refill the NA values with NA color
	for r in range(0,nrows):
		for c in range(0,ncols):
			
		
			x=c-0.5
			y=r-0.5
			m=masks[r][c]
			if m==0:
				#need to fill:
				#print >> stderr,"NA at",r,c
				#broken_barh([(x,1)],(y,1),facecolor=options.NAColor,linewidth=0.0,antialiased=True) #edgecolor=options.NAColor,
				gca().add_patch(Rectangle((x,y),1,1,facecolor=options.NAColor,linewidth=0.0))
				plot([x,x+1],[y,y+1],color="black")
				plot([x,x+1],[y+1,y],color="black")
				
	for r in range(1,nrows):
		axhline(y=r-0.5,color="white",linewidth=1.5)
	for c in range(1,ncols):
		axvline(x=c-0.5,color="white",linewidth=1.5)
	
	#now set labels:
	xticks(arange(ncols),colnames)
	yticks(arange(nrows),rownames)
	xlim(-0.5,ncols-0.5)
	ylim(-0.5,nrows-0.5)	
	
	
	
	if options.figSize:
		gcf().set_size_inches(float(options.figSize[0]),float(options.figSize[1]))
		
	fw,fh=gcf().get_size_inches()
	
	shrink=1.0/(max(fw,fh)/6.0*2.0)
		
	colorbar(shrink=shrink)
	savefig(figFileName)
	

if __name__=='__main__':
	parser=OptionParser("usage:\t%prog [options] matrixFile outputFigFilename\n\t%prog --show-available-color-maps outputFigFilename")
	parser.add_option("--xtick-rotation",dest="xtickRotation",default=0.0,type=float,help="specify rotation of xticks in degrees [0.0]")
	parser.add_option("--color-map",dest="colormapName",default="gnuplot2",help="specify color map")
	parser.add_option("--show-available-color-maps",dest="showAvailableColorMap",action="store_true",default=False,help="show the color maps to output filename")
	parser.add_option("--NA-color",dest="NAColor",default="grey",help="set NA data color [grey]")
	parser.add_option("--data-range",dest="dataRange",default=None,nargs=2,help="set data range --data-range min max [default: None: Auto]")
	parser.add_option("--fs",dest="fs",default="\t",help="set field separator [tab]")
	parser.add_option('--fig-size',dest='figSize',default=None,nargs=2,help="set figure dimension --fig-size w h [default: None: Auto]")
	(options, args) = parser.parse_args(argv)
	


	if options.showAvailableColorMap:
		try:
			outFigFile,=args[1:]
		except:
			parser.print_help()
			exit()
		showAvailableColorMapToFigure(outFigFile)
		
	
	else:
		try:
			inFile,outFigFile=args[1:]
			
		except:
			parser.print_help()
			exit()
		plotColorMatrix(inFile,outFigFile,options)
		
	

