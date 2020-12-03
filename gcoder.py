from tkinter import *
from tkinter import Menu
from tkinter import filedialog
from array import *

import os
import math
import sys
import datetime
import tkinter as tk1

#	------------------------------------------------------
#	Class GCoder:	Maintains and modifies info in nc file
#					Also displays useful info to the user 
#	------------------------------------------------------
#	TODO:
#		Add 3D display of router path and stock
#			(In separate window?)
#		Clean-up main window display
#		Improve estimateTime by adding time for 
#			direction change and Z movement
#
#	Methods:
#		adjustF(self)
#		adjustZ(self)
#		applyF(self)
#		applyZ(self)
#		closePage(self)
#		estimateTime(self)
#		getDist(self,x1,y1,z1,x2,y2,z2)
#		getRanges(self)
#		ListZHeights(self)
#		openFile(self)
#		saveAs(self)
#		ShowGrid(self)
#		ShowMenu(self)

class GCoder():
	fileName = 'No File Loaded Yet. In the menu, use "File"-"Open G-Code\nOr ctrl-o" to get started'
	FileLoaded = False
	FileDirty = False
	LineList = []
	zlist = []
	zval = []
	flist = []
	fval = []
	zlistLoaded = False
	NumLines = 0
	NumMoves = ''
	NumMovesG0 = 0
	NumMovesG1 = 0
	UOM = 'mm'
	EstRunTime = '--:--:--'
	MaxX = 0.0
	MinX = 0.0
	MaxY = 0.0
	MinY = 0.0
	MaxZ = 0.0
	MinZ = 0.0
	MaxF = 0.0
	MinF = 0.0
	RunTime = 0.0
	Menu = ''
	tk = Tk()
	zflds = {}
	fflds = {}


	def __init__(self):
		print('__init__')

		winWidth = int(self.tk.winfo_screenwidth() / 2)
		winHeight = int(self.tk.winfo_screenheight() / 2)
		width = self.tk.winfo_screenwidth()
		height = self.tk.winfo_screenheight()
		frm_width = self.tk.winfo_rootx() - self.tk.winfo_x()
		win_width = self.tk.winfo_width() + (2*frm_width)
		titlebar_height = self.tk.winfo_rooty() - self.tk.winfo_y()
		win_height = self.tk.winfo_height() + (titlebar_height + frm_width)
		x = int((width - winWidth) / 2)
		y = int((height - winHeight) / 2)
		self.tk.geometry(f'{winWidth}x{winHeight}+{x}+{y}')
		self.FileLoaded = False
		
		self.tk.title("NC Info")
	
	def ShowGrid(self):
		print('ShowGrid start')
		
		for cell in self.tk.grid_slaves():
			cell.grid_forget()
		
		FileNameLbl = Label(self.tk, text="File:", font=("Arial",10))
		FileNameLbl.config(highlightbackground='black',highlightthickness=2)
		FileNameLbl.grid(column=0,row=0,sticky="NE")
		fileName = Label(self.tk, text=self.fileName, font=("Arial",10))
		fileName.grid(column=1,row=0,sticky="NW")

		SizeNameLbl = Label(self.tk, text="# Lines:", font=("Arial",10))
		SizeNameLbl.grid(column=0,row=1,sticky="NE")
		SizeValue = Label(self.tk, text=self.NumLines, font=("Arial",10))
		SizeValue.grid(column=1,row=1,sticky="NW")

		MovesNameLbl = Label(self.tk, text="# Moves:", font=("Arial",10))
		MovesNameLbl.grid(column=0,row=2,sticky="NE")
		MovesValue = Label(self.tk, text=self.NumMoves, font=("Arial",10))
		MovesValue.grid(column=1,row=2,sticky="NW")

		UOMNameLbl = Label(self.tk, text="Unit of measurement:", font=("Arial",10))
		UOMNameLbl.grid(column=0,row=3,sticky="NE")
		UOMValue = Label(self.tk, text=self.UOM, font=("Arial",10))
		UOMValue.grid(column=1,row=3,sticky="NW")

		totTimeLbl = Label(self.tk, text="Estimated Time:", font=("Arial",10))
		totTimeLbl.grid(column=0,row=6,sticky="NE")
		totTimeVal = Label(self.tk, text = self.EstRunTime, font=("Arial",10))
		totTimeVal.grid(column=1,row=6,sticky="NW")

		MinNameLbl = Label(self.tk, text="Min:", font=("Arial",10))
		MinNameLbl.grid(column=2,row=1,sticky="NE")
		MaxNameValue = Label(self.tk, text="Max:", font=("Arial",10))
		MaxNameValue.grid(column=2,row=2,sticky="NE")

		XLbl = Label(self.tk, text="X", font=("Arial",10))
		XLbl.grid(column=3,row=0,sticky="N")
		YLbl = Label(self.tk, text="Y", font=("Arial",10))
		YLbl.grid(column=4,row=0,sticky="N")
		ZLbl = Label(self.tk, text="Z", font=("Arial",10))
		ZLbl.grid(column=5,row=0,sticky="N")
		FLbl = Label(self.tk, text="F", font=("Arial",10))
		FLbl.grid(column=6,row=0,sticky="N")
		
		xmVal = Label(self.tk, text=self.MinX, font=("Arial",10))
		xmVal.grid(column=3,row=1, sticky="NE")
		xxVal = Label(self.tk, text=self.MaxX, font=("Arial",10))
		xxVal.grid(column=3,row=2, sticky="NE")

		ymVal = Label(self.tk, text=self.MinY, font=("Arial",10))
		ymVal.grid(column=4,row=1, sticky="NE")
		yxVal = Label(self.tk, text=self.MaxY, font=("Arial",10))
		yxVal.grid(column=4,row=2, sticky="NE")

		zmVal = Label(self.tk, text=self.MinZ, font=("Arial",10))
		zmVal.grid(column=5,row=1, sticky="NE")
		zxVal = Label(self.tk, text=self.MaxZ, font=("Arial",10))
		zxVal.grid(column=5,row=2, sticky="NE")

		fmVal = Label(self.tk, text=self.MinF, font=("Arial",10))
		fmVal.grid(column=6,row=1, sticky="NE")
		fxVal = Label(self.tk, text=self.MaxF, font=("Arial",10))
		fxVal.grid(column=6,row=2, sticky="NE")

		if self.zlistLoaded == True:
			frame1 = Frame(self.tk,relief="raised")
			frame1.grid(column=1,row=11,sticky="N", columnspan=8)
			
			zl0 = Label(frame1, text = 'Z Values Found', font=("Arial",10))
			zl0.grid(column=1,row=10, sticky="N", columnspan=3)
			rowno = 11
			lineno = 0
			for line in self.zlist:
				tmp = Label(frame1, text = "{0:.2f}".format(line), font=("Arial",10))
				tmp.grid(column=1,row=rowno, sticky="NE")
				tmp = Label(frame1, text = " => ", font=("Arial",10))
				tmp.grid(column=2,row=rowno, sticky="N")
				self.zflds[lineno] = tk1.StringVar()
				self.zflds[lineno].set(line)
				tmp = Entry(frame1,width=10,textvariable=self.zflds[lineno])
				tmp.grid(column=3,row=rowno, sticky="NE")
				rowno += 1
				lineno += 1

			MaxRowNum = rowno
			
			fl0 = Label(frame1, text='F Values Found', font=("Arial",10))
			fl0.grid(column=5,row=10, sticky="N", columnspan=3)
			rowno = 11
			lineno = 0
			for line in self.flist:
				tmp = Label(frame1, text="{0:.0f}".format(line), font=("Arial",10))
				tmp.grid(column=5,row=rowno, sticky="NE")
				tmp = Label(frame1, text = " => ", font=("Arial",10))
				tmp.grid(column=6,row=rowno, sticky="N")
				self.fflds[lineno] = tk1.StringVar()
				self.fflds[lineno].set("{0:d}".format(int(line)))
				tmp = Entry(frame1,width=10,textvariable=self.fflds[lineno])
				tmp.grid(column=7,row=rowno, sticky="NE")
				rowno += 1
				lineno += 1
			
			if rowno > MaxRowNum:
				MaxRowNum = rowno
				
			btns = Frame(frame1)
			btns.grid(column=0,row=MaxRowNum+1,columnspan=7)
			tmp = Button(btns,text="Apply To Z",bd=5,command=self.applyZ)
			tmp.grid(column=0,row=0,sticky="NW",columnspan=3)
			tmp = Button(btns,text="Apply To F",bd=5,command=self.applyF)
			tmp.grid(column=5,row=0,sticky="NE",columnspan=3)

	def doDebug(self):
		lineno = 0
		print('Debug start')
		for line in self.zlist:
			print( format(lineno) + ") Swap Z" + format(line) + " for Z" + format(self.zflds[lineno].get()))
			lineno += 1

		lineno = 0
		for line in self.flist:
			print( format(lineno) + ") Swap F" + format(line) + " for F" + format(self.fflds[lineno].get()))
			lineno += 1

		print('Debug end')


	def applyZ(self):
		# Apply new values to Z in file
		print("ApplyZ")
		self.adjustZ()

	def applyF(self):
		# Apply new values to F in file
		print("ApplyF")
		self.adjustF()

	def key_openFile(self,event):
		print("key_openFile()")
		self.openFile()
		
	def key_saveAs(self,event):
		print("key_saveAs()")
		self.saveAs()
		
	def key_closePage(self,event):
		self.closePage()

	def ShowMenu(self):
		print("ShowMenu() start")
		menu = Menu(self.tk)

		FileMenu = Menu(menu, tearoff=0)

		FileMenu.add_command(label='Open G-Code File', command=self.openFile, underline=0)
		self.tk.bind('<Control-o>',self.key_openFile)
		FileMenu.add_command(label='Save As', underline=5, command=self.saveAs)
		if self.FileLoaded == True:
			self.tk.bind('<Control-a>',self.key_saveAs)
			
		FileMenu.add_separator()
		FileMenu.add_command(label='Exit', underline=1, command=self.closePage)
		self.tk.bind('<Control-x>',self.key_closePage)
		print("ShowMenu() filemenu end")

		ToolMenu = Menu(menu, tearoff=0)

		ToolMenu.add_command(label='View Tool Path', underline=5)
		ToolMenu.add_command(label='View Stock', underline=5)

		ConfigMenu = Menu(menu, tearoff=0)

		ConfigMenu.add_command(label='Tools', underline=0)
		ConfigMenu.add_command(label='Material Size/Type', underline=0)

		HelpMenu = Menu(menu, tearoff=0)

		HelpMenu.add_command(label='Documentation', underline=0)
		HelpMenu.add_command(label='About', underline=0)

		menu.add_cascade(label='File', menu=FileMenu, accelerator='Alt+f')
		menu.add_cascade(label='Tools', menu=ToolMenu, accelerator='Alt+t')
		menu.add_cascade(label='Config', menu=ConfigMenu, accelerator='Alt+c')
		menu.add_cascade(label='Help', menu=HelpMenu, accelerator='Alt+h')
		if self.FileLoaded == True:
			menu.entryconfig('Config', state='normal')
			menu.entryconfig('Tools', state='normal')
			FileMenu.entryconfig('Save As',state='normal')
			if self.FileDirty == True:
				FileMenu.entryconfig('Save As',state='normal')
			else:
				FileMenu.entryconfig('Save As',state='disabled')
				self.tk.unbind('<Control-a>')
		else:
			menu.entryconfig('Config', state='disabled')
			menu.entryconfig('Tools', state='disabled')
			FileMenu.entryconfig('Save As',state='disabled')

		self.tk.config(menu=menu)
		print("ShowMenu() end")


	def openFile(self):
		print("openFile()")
		self.Menu = ''
		self.MeasureSystem = "unknown"
		self.NumMovesG0 = 0
		self.NumMovesG1 = 0
		self.SizeValue = ''
		self.NumLines = 0
		self.EstRunTime = 0.0
		self.MinXValue = 10000
		self.MaxXValue = 0
		self.MinYValue = 10000
		self.MaxYValue = 0
		self.MinZValue = 10000
		self.MaxZValue = 0
		self.MinFValue = 10000
		self.MaxFValue = 0
		self.zlist = []
		self.LineList = []

		NewFileName = filedialog.askopenfilename(filetypes = (("G-Code files","*.nc"),("all files","*.*")),initialdir='C:\Proj_Src\Woodworking Projects\Wedgie')
		self.fileName = NewFileName
		FileName = Label(self.tk, text=NewFileName, font=("Arial",10))
		FileName.grid(column=1,row=0)
		CurrFileObj = open(NewFileName,"r")

		for line in CurrFileObj:
			self.LineList.append(line)
		
		CurrFileObj.close()
		self.getRanges()
		
		self.zlistLoaded = False
		self.NumMoves = "G0: "+format(self.NumMovesG0)+", G1: "+format(self.NumMovesG1)
		self.FileLoaded = True
		self.estimateTime()
		self.ShowMenu()
		self.ShowGrid()

	def getRanges(self):
		print("getRanges()")
		for line in self.LineList:
			line = line.strip(' \r\n')
			words = line.split(" ")
			if words[0] == 'G0':
				self.NumMovesG0 += 1
			if words[0] == 'G1':
				self.NumMovesG1 += 1
			if words[0] == 'G20':
				self.MeasureSystem = "inches"
			if words[0] == 'G21':
				self.MeasureSystem = "millimeters"
				
			self.NumLines += 1
			for arg in words:
				if arg.startswith('X'):
					if float(arg[1:]) > self.MaxX:
						self.MaxX = float(arg[1:])
					if float(arg[1:]) < self.MinX:
						self.MinX = float(arg[1:])
				elif arg.startswith('Y'):
					if float(arg[1:]) > self.MaxY:
						self.MaxY = float(arg[1:])
					if float(arg[1:]) < self.MinY:
						self.MinY = float(arg[1:])
				elif arg.startswith('Z'):
					if float(arg[1:]) > self.MaxZ:
						self.MaxZ = float(arg[1:])
					if float(arg[1:]) < self.MinZ:
						self.MinZ = float(arg[1:])
				elif arg.startswith('F'):
					if float(arg[1:]) > self.MaxF:
						self.MaxF = float(arg[1:])
					if float(arg[1:]) < self.MinF:
						self.MinF = float(arg[1:])

	def saveAs(self):
		print('saveAs START')
		newFileName = filedialog.asksaveasfilename(title='Save NC (GCode) File',initialfile=self.fileName,filetypes=(("G-Code File","*.nc"),("All Files","*.*")),defaultextension='nc')
		if newFileName != "":
			fhandel = open(newFileName,'w')
			for line in self.LineList:
				fhandel.write(line+'\n')
			fhandel.close()
			self.fileName = newFileName
		print('saveAs END')
		
	def closePage(self):
		print('closePage')
		quit()
	
	def getDist(self,x1,y1,z1,x2,y2,z2):
		dist = math.sqrt(math.pow((x1-x2),2) + math.pow((x1-x2),2))
		dist += z1 - z2
		return dist

	def estimateTime(self):
		print("estimateTime()")
		runTime = 0.0
		travel = 0.0
		newX = 0.0
		lastX = 0.0
		newY = 0.0
		lastY = 0.0
		newZ = 0.0
		lastZ = 0.0
		newF = 0.0
		lastF = 1000.0
		line = ''
		words = []
		arg = []

		
		for line in self.LineList:
			line = line.strip(' \r\n')
			words = line.split(" ")
			if words[0] == 'G0':
				moved = 1
			if words[0] == 'G1':
				moved = 1
			if words[0] == 'G20':
				MeasureSystem = "in"
			if words[0] == 'G21':
				MeasureSystem = "mm"
			for arg in words:
				if arg.startswith('X'):
					newX = float(arg[1:])
					if MeasureSystem == 'in':
						newX = newX * 25.4
				elif arg.startswith('Y'):
					newY = float(arg[1:])
					if MeasureSystem == 'in':
						newY = newY * 25.4
				elif arg.startswith('Z'):
					newZ = float(arg[1:])
					if MeasureSystem == 'in':
						newZ = newZ * 25.4
				elif arg.startswith('F'):
					newF = float(arg[1:])
					if MeasureSystem == 'in':
						newF = newF * 25.4
			if newX != lastX or newY != lastY or newZ != lastZ:
				travel = self.getDist(newX,newY,newZ,lastX,lastY,lastZ)
				if lastF != 0:
					runTime += abs(travel) / (lastF / 60.0)
				elif newF != 0:
					runTime += abs(travel) / (newF / 60.0)
				
			lastX = newX
			lastY = newY
			lastZ = newZ
			lastF = newF
		
		self.ListZHeights()
		self.zlistLoaded = True
		totTime1 = runTime
		totTime2 = runTime * 1.1
		rt = 'Between ' + str(datetime.timedelta(seconds=int(totTime1))) + ' and ' + str(datetime.timedelta(seconds=int(totTime2))) + ' d h:m:s (approximately)'
		self.EstRunTime = rt
		self.ShowGrid()
		

	def ListZHeights(self):
		self.zlist = []
		self.flist = []
		rowno = 0
		for line in self.LineList:
			line = line.strip(' \r\n')
			words = line.split(" ")
			if words[0] == 'G0' or words[0] == 'G1':
				for arg in words:
					if arg.startswith('Z'):
						newZ = float(arg[1:])
						if (not newZ in self.zlist) or (len(self.zlist) == 0):
							self.zlist.append(newZ)
#							print(format(rowno) + ') append to z ' + format(newZ))
					elif arg.startswith('F'):
						newF = float(arg[1:])
						if (not newF in self.flist) or (len(self.flist) == 0):
							self.flist.append(newF)
#							print(format(rowno) + ') append to f ' + format(newF))
			rowno += 1
		
		self.zlist.sort(reverse=True)
		self.zlistLoaded = True
		self.flist.sort(reverse=True)

	def adjustZ(self):
		print("adjustZ()")
		cnt = 0
		newFile = []
		for line in self.LineList:
			cnt += 1
			line = line.strip(' \r\n')
			newline = line
			words = line.split(" ")
			if words[0] == 'G0' or words[0] == 'G1':
				for arg in words:
					if arg.startswith('Z'):
#						print(self.zlist)
#						print('self.zflds')
#						for item in self.zflds:
#							print(item)
						val = arg[1:]
						tvl = self.zlist[self.zlist.index(float(val))]
						tvlF = '{0:.4f}'.format(self.zlist[self.zlist.index(float(val))])
						idx = self.zlist.index(float(val))
#						print(tvl,tvlF,idx)
						newval = self.zflds[idx].get()
#						print('Orig Line: ' + line)
						newline = words[0] + ' Z' + '{0:.4f}'.format(float(newval))
						for args in words:
							if (not args.startswith('G')) and (not args.startswith('Z')):
								newline += ' ' + args
#						print(' New Line: ' + newline)
			newFile.append(newline)
		self.LineList = newFile
		self.FileDirty = True
		self.getRanges()
		self.estimateTime()
		self.ShowMenu()
		self.ShowGrid()


	def adjustF(self):
		print("adjustF()")
		cnt = 0
		newFile = []
		for line in self.LineList:
			cnt += 1
			line = line.strip(' \r\n')
			newline = line
			words = line.split(" ")
			if words[0] == 'G0' or words[0] == 'G1':
				for arg in words:
					if arg.startswith('F'):
#						print(self.flist)
#						print('self.fflds')
#						for item in self.fflds:
#							print(item)
						val = arg[1:]
						tvl = self.flist[self.flist.index(float(val))]
						tvlF = '{0:.4f}'.format(self.flist[self.flist.index(float(val))])
						idx = self.flist.index(float(val))
#						print(tvl,tvlF,idx)
						newval = self.fflds[idx].get()
#						print('Orig Line: ' + line)
						newline = words[0] + ' F' + '{0:d}'.format(int(newval))
						for args in words:
							if (not args.startswith('G')) and (not args.startswith('F')):
								newline += ' ' + args
#						print(' New Line: ' + newline)
			newFile.append(newline)
		self.LineList = newFile
		self.FileDirty = True
		self.getRanges()
		self.estimateTime()
		self.ShowMenu()
		self.ShowGrid()



#	def ShowPaths():
	
#	def ShowStock():
	

tmp = GCoder()

tmp.ShowMenu()
tmp.ShowGrid()


tmp.tk.mainloop()