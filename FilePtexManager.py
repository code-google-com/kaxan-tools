from PyQt4 import QtGui,QtCore
import maya.cmds as cmds
import PyQt4.uic
import os
from pprint import pprint as pp
import os2emxpath
import csv
#import maya.mel as mel
#import pymel.core as pm
#-----------PYQT UTF-8-------------------
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
#--------------Script Dir for UIs Loading UI---------------
myScriptDir = cmds.internalVar(userScriptDir=True)
uifile = myScriptDir+'FileManager.ui'
form, base = PyQt4.uic.loadUiType(uifile)
#--------------Initiating Class------------------------
class FilesManager(base, form):
    def __init__(self):
        super(base,self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        #QtCore.QObject.connect(self.treeWidget, QtCore.SIGNAL(_fromUtf8("customContextMenuRequested(QPoint)")), MainWindow.rightClick)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.checkFiles()#<-------Updates TreeWidget
	self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
	self.treeWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
	#self.treeWidget.grabKeyboard()
    def keyPressEvent(self,event):
	#QtGui.QWidget.keyPressEvent(self, event)
	
        self.treeWidget.keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Delete:
	    itemsSelected = self.treeWidget.selectedItems()
	    for x in itemsSelected:
		    if (cmds.referenceQuery(str(x.text(0)), isNodeReferenced=True)) == True:
			    cmds.warning( "You can't delete referenced nodes."  )
			    QtCore.QEvent.accept(event)
			    pass
		    else:
		    	index = QtGui.QTreeWidget.indexOfTopLevelItem(self.treeWidget, x)
			cmds.delete(str(x.text(0)))
		    	QtGui.QTreeWidget.takeTopLevelItem(self.treeWidget, index)
			#cmds.select(str(x.text(0)),add= True)
			QtCore.QEvent.accept(event)
			
        if event.key() == QtCore.Qt.Key_Backspace:
	    itemsSelected = self.treeWidget.selectedItems()
	    for x in itemsSelected:
		    if (cmds.referenceQuery(str(x.text(0)), isNodeReferenced=True)) == True:
			    cmds.warning( "You can't delete referenced nodes."  )
			    QtCore.QEvent.accept(event)
			    pass
		    else:
		    	index = QtGui.QTreeWidget.indexOfTopLevelItem(self.treeWidget, x)
			cmds.delete(str(x.text(0)))
		    	QtGui.QTreeWidget.takeTopLevelItem(self.treeWidget, index)
			#cmds.select(str(x.text(0)),add= True)
			QtCore.QEvent.accept(event)
    def SelectAll(self):        
        self.treeWidget.selectAll()
    def rightClick(self,point):
        # Create a menu
        menu = QtGui.QMenu("Menu", self)
        #menu.addAction(self.menuFile.menuAction())
        menu.addAction(self.actionReplace_selected)
        menu.addAction(self.actionSearch_and_replace_selected)
        #menu.addAction(self.actionImport_CSV)
        # Show the context menu.
        menu.exec_(self.treeWidget.mapToGlobal(point))
        #itemSelected = self.treeWidget.currentItem()
        print point
        
#--------------ExportCSV: Esport table as CSV
    def exportCSV(self):
        sceneDir = os.path.dirname(cmds.file(q=True, sn=True))                
        fileName = QtGui.QFileDialog.getSaveFileName(self, ("Export CSV"), sceneDir, ("CSV File (*.csv)") , None, QtGui.QFileDialog.DontConfirmOverwrite)

            
        if not fileName:
            pass
        elif os.path.isfile(fileName) == True:
            msgBox = QtGui.QMessageBox(self)
            msgBox.setText("Overwrite or Append only server paths?")
            #msgBox.setInformativeText("Replace Items based on?")
            msgBox.setIcon(QtGui.QMessageBox.Question)
            msgBox.addButton(self.tr("Ove.rwrite"), QtGui.QMessageBox.ActionRole)
            msgBox.addButton(self.tr("Append"), QtGui.QMessageBox.ActionRole)
            #msgBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            msgBox.setWindowTitle("File Already Exist")
            msgBox.setDetailedText("Append will only append nodes that are not already on CSV, and are mounted on a server"  )
            #msgBox.setStandardButtons(self.tr("Index"), self.tr("Node Name"))
            basedOn = msgBox.exec_()
            if basedOn == 1:
                montados = []
                for x in AllFiles:
                    if os.path.splitunc(x[2])[0]:
                        montados.append(x)
                importados = []
                with open(fileName) as f:
                    reader = csv.reader(f)
                    for row in f:
                        importados.append(row)    
                for x in montados:
                    bandera = False
                    for y in importados:
                        if (x[0]) in y:
                            print 'El nodo "', (x[0]), '" esta en importados, skiping'
                            bandera = True
                    if bandera == False:
                        print 'El nodo "', (x[0]), '" no esta en importados, anexado' 
                        with open(fileName, 'ab') as f:
                            writer = csv.writer(f, dialect='excel', quoting=csv.QUOTE_ALL)
                            writer.writerow(x)
            elif basedOn == 0:                
                with open(fileName, 'wb') as f:
                    writer = csv.writer(f, dialect='excel', quoting=csv.QUOTE_ALL)
                    writer.writerows(AllFiles)        
        else:
            with open(fileName, 'wb') as f:
                writer = csv.writer(f, dialect='excel', quoting=csv.QUOTE_ALL)
                writer.writerows(AllFiles)
#--------------importCSV: import CSV to maya replacing paths and node names-----------
    def importCSV(self):
        sceneDir = os.path.dirname(cmds.file(q=True, sn=True))                
        fileName = QtGui.QFileDialog.getOpenFileName(self, ("Export CSV"), sceneDir, ("CSV File (*.csv)") , None, )
        if not fileName:
            pass
        else:
            with open(fileName, 'rb') as f:
                reader = csv.reader(f)
                importedFiles = []
                for row in reader:
                    importedFiles.append(row)
            msgBox = QtGui.QMessageBox(self)
            msgBox.setText("Update items based on?")
            #msgBox.setInformativeText("Replace Items based on?")
            msgBox.setIcon(QtGui.QMessageBox.Question)
            msgBox.addButton(self.tr("Index"), QtGui.QMessageBox.ActionRole)
            msgBox.addButton(self.tr("Node Name"), QtGui.QMessageBox.ActionRole)
            #msgBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            msgBox.setWindowTitle("hola")
            msgBox.setDetailedText("Use INDEX if you changed NodeNames, but you havent deleted nodes.\n" + "Use NODENAME if you deleted nodes, but you havent changed NodeNames."  )
            #msgBox.setStandardButtons(self.tr("Index"), self.tr("Node Name"))
            basedOn = msgBox.exec_()
            #basedOn = QtGui.QMessageBox.question(self, self.tr("Confirm"), self.tr("\n" + "Replace Items based on?"), self.tr("Index"), self.tr("Node Name") )
            if basedOn == 0:                                    
                    for x, y in enumerate(items):            
                        try:
                            cmds.setAttr(str(y.text(0)+".ptexFile"), os2emxpath.normpath(str((importedFiles[x][2])+'\\'+(importedFiles[x][1]))), type="string")
                            cmds.rename(str(y.text(0)), str(importedFiles[x][0]))
                        except RuntimeError:
                            cmds.setAttr(str(y.text(0)+".fileTextureName"), os2emxpath.normpath(str((importedFiles[x][2])+'\\'+(importedFiles[x][1]))), type="string")
                            cmds.rename(str(y.text(0)), str(importedFiles[x][0]))
                        else:
                            pass
            if basedOn == 1:                                                           
                for x in importedFiles:
                    if x[3] == "VRayPtex":                            
                        try:
                            cmds.setAttr(str((x[0])+".ptexFile"), os2emxpath.normpath(str((x[2])+'\\'+(x[1]))), type="string")
                        except:
                            pass
                    if x[3] == "file":
                        try:
                            cmds.setAttr(str((x[0])+".fileTextureName"), os2emxpath.normpath(str((x[2])+'\\'+(x[1]))), type="string")
                        except:
                            pass

            self.checkFiles()           
#------------Adding the filepaths to TreeWidget--------
    def Refresh(self):
        self.treeWidget.clear()#<-------Removing Items if any---------
        PtextFileNodes = cmds.ls (type = "VRayPtex")  #------------Adding Vray File Nodes
        PtexFiles = []
        for x, y in enumerate(PtextFileNodes):
            PtexFiles.append([y])
            PtexFiles[x].extend([os.path.basename(os.path.normpath(cmds.getAttr(y+".ptexFile")))])
            PtexFiles[x].extend([os.path.dirname(os.path.normpath(cmds.getAttr(y+".ptexFile")))])
            PtexFiles[x].extend([cmds.nodeType(y)])
        FileNodes = cmds.ls (type = "file")   #<----------adding File Nodes-----------
        NodeFiles = []
        for x,y in enumerate(FileNodes):
            NodeFiles.append([y])
            NodeFiles[x].extend([os.path.basename(os.path.normpath(cmds.getAttr(y+".fileTextureName")))])
            NodeFiles[x].extend([os.path.dirname(os.path.normpath(cmds.getAttr(y+".fileTextureName")))])
            NodeFiles[x].extend([cmds.nodeType(y)])            
        global AllNodes
        AllNodes = PtextFileNodes + FileNodes
        global AllFiles
        AllFiles = PtexFiles + NodeFiles
        global items
        items = []
        for i in AllFiles:
            items.append(QtGui.QTreeWidgetItem(i))
        self.treeWidget.addTopLevelItems(items)  #<----------adding filepaths to treewidget--------
	self.treeWidget.setColumnWidth(0, 90)
	self.treeWidget.setColumnWidth(1, 120)
	self.treeWidget.resizeColumnToContents(2)
	self.treeWidget.setColumnWidth(3, 50)

        self.SearchItem(self)
#----------Check Files:  Checks if files exists, if not, paint items red, first checks path then file-----------
    def checkFiles(self):
        QtCore.QObject.disconnect(self.treeWidget, QtCore.SIGNAL(_fromUtf8("itemChanged(QTreeWidgetItem*,int)")), self.textEdit)#<-----disconnects itemchanged signal to avoid recursive infinite loops
        self.Refresh()#<-----add items
        for x in items:
            if not os.path.isdir(str(x.text(2))):#<--------checks if path exists first (from the treewidget)
                x.setBackground(2, QtGui.QBrush(QtGui.QColor(255,0,0)))
                x.setForeground(0, QtGui.QBrush(QtGui.QColor(255,0,0)))
                x.setForeground(1, QtGui.QBrush(QtGui.QColor(255,0,0)))
                x.setForeground(3, QtGui.QBrush(QtGui.QColor(255,0,0)))
            elif not os.path.isfile(os.path.normpath(os.path.join(str(x.text(2)),str(x.text(1))))):#<-------then it checks if file exists
                x.setBackground(1, QtGui.QBrush(QtGui.QColor(255,0,0)))
                x.setForeground(0, QtGui.QBrush(QtGui.QColor(255,0,0)))
                x.setForeground(2, QtGui.QBrush(QtGui.QColor(255,0,0)))
                x.setForeground(3, QtGui.QBrush(QtGui.QColor(255,0,0)))
        QtCore.QObject.connect(self.treeWidget, QtCore.SIGNAL(_fromUtf8("itemChanged(QTreeWidgetItem*,int)")), self.textEdit)#<------reconnecting signal
        
#----------#Click Select:  selects Nodes in Maya selected in treewidget-------
    def ClickSelect(self):
        itemsSelected = self.treeWidget.selectedItems()
        cmds.select(clear=True)
        if itemsSelected:
           for x in itemsSelected:
                cmds.select(str(x.text(0)),add= True)       
        #cmds.select(str(QtGui.QTreeWidgetItem.text(item,0)))
#-------------------Search Module/Hiddes all items, unhides find ones------------------------------------------------
    def SearchItem(self, name):
        #print extra
        #name = self.searchLineEdit.displayText()
        SearchIn = (self.SearchInComboBox.currentIndex())
        try:            
            if SearchIn == 0:#<-------Search All Fields
                itemsNuevos = QtGui.QTreeWidget.findItems(self.treeWidget, name, QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive, 0)
                itemsNuevos.extend(QtGui.QTreeWidget.findItems(self.treeWidget, name, QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive, 1))
                itemsNuevos.extend(QtGui.QTreeWidget.findItems(self.treeWidget, name, QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive, 2))
            elif SearchIn == 1:#<-----------Search NodeName
                itemsNuevos = QtGui.QTreeWidget.findItems(self.treeWidget, name, QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive, 0)
            elif SearchIn == 2:#<---------Search FileName
                itemsNuevos = QtGui.QTreeWidget.findItems(self.treeWidget, name, QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive, 1)
            elif SearchIn == 3:#<--------Search PathName
                itemsNuevos = QtGui.QTreeWidget.findItems(self.treeWidget, name, QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive, 2)
            for item in QtGui.QTreeWidget.findItems(self.treeWidget,"", QtCore.Qt.MatchContains):#<------hiddes all items
                item.setHidden(True)
            for item in itemsNuevos:#<---- shows find items
                item.setHidden(False)
        except:
            pass            
                
           

#-------------Text Edits, editing text in treewidget changes node names and paths in Maya--------------------------
    def textEdit(self,item,column):
        NewName = []
        NewName = QtGui.QTreeWidgetItem.text(item,column)
        type = QtGui.QTreeWidgetItem.text(item,3)
        if type == "VRayPtex":
            if column == 0:
                cmds.rename (str(NodeName), str(NewName))
            elif column == 1:
                cmds.setAttr(str(QtGui.QTreeWidgetItem.text(item,0)+".ptexFile"), os2emxpath.normpath(str(QtGui.QTreeWidgetItem.text(item,2)+'\\'+NewName)), type="string")
            elif column == 2:
                cmds.setAttr(str(QtGui.QTreeWidgetItem.text(item,0)+".ptexFile"), os2emxpath.normpath(str((NewName)+'\\'+QtGui.QTreeWidgetItem.text(item,1))), type="string")
        elif type == "file":
            if column == 0:
                cmds.rename (str(NodeName), str(NewName))
            elif column == 1:
                cmds.setAttr(str(QtGui.QTreeWidgetItem.text(item,0)+".fileTextureName"),  os2emxpath.normpath(str(QtGui.QTreeWidgetItem.text(item,2)+'\\'+NewName)), type="string")
            elif column == 2:
                cmds.setAttr(str(QtGui.QTreeWidgetItem.text(item,0)+".fileTextureName"), os2emxpath.normpath(str((NewName)+'\\'+QtGui.QTreeWidgetItem.text(item,1))), type="string")
        self.checkFiles()#<------Updates TreeWidget---------
#------------edit item:  double click edits item, first i was making all items editable but i prefer doing it manually for each one so I can hace specific options
    def editItem(self,item,column):
        QtCore.QObject.disconnect(self.treeWidget, QtCore.SIGNAL(_fromUtf8("itemChanged(QTreeWidgetItem*,int)")), self.textEdit)#<-----disconnects itemchanged signal to avoid recursive infinite loops
        global NodeName
        NodeName = QtGui.QTreeWidgetItem.text(item,0)#<--------Sends the original Node Name to Global---------
        if column == 3: #<---------Cant edit Type---------
            pass
        else:
            item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsSelectable)#<---------changing flags------
            QtGui.QTreeWidget.editItem(self.treeWidget,item,column)
        QtCore.QObject.connect(self.treeWidget, QtCore.SIGNAL(_fromUtf8("itemChanged(QTreeWidgetItem*,int)")), self.textEdit)#<-----reconnects itemchanged signal
#-------Replace: replaces File in Node, calling a file dialog-----------
    def replace(self):
        itemsSelected = self.treeWidget.selectedItems()
        #itemSelected = self.treeWidget.currentItem()
        if not itemsSelected:
            pass
        else:
            fileName = QtGui.QFileDialog.getOpenFileName(self, ("Open Image"), "", ("All Files (*);;Alias PIX Files (*.als *.pix);;AVI Files (*.avi *.vdr *.wav);;Cineon files (*.cin *.kdk);;DirectShow Files (*.asf *.avi *.mpe *.mpg *.mpeg *.vob *.wmv);;DPS HVD Files (*.hvd);;DPX Files (*.dpx);;DVA Files (*.dva);;FITS Files (*.fits *.fts);;Flexible Precision Image Files (*.flx);;Fusion Flipbooks (*.fb);;Fusion Raw Image Files(*.raw);;Fusion x64 Tutorial Files (*.dft);;IFF Files (*.iff *.ilbm *.ilm *.ibm);;IFL Files (*.ifl);;IPL Files (*.ipl);;JPEG Files (*.jpg *.jpeg);;JPEG2000 Files (*.jp2);;Maya IFF Files (*.iff);;OMF Interchange Files (*.omf *.omfi);;OpenEXR Files (*.exr *.sxr);;Pandora YUV Files (*.piyuv10);;Photoshop PSD Files (*.psd);;PNG Files (*.png);;Quantel VPB Files (*.vpb *.qtl);;Radiance HDR Files (*.hdr *.rgbe);;RED RAWCODE Files (*.r3d);;Rendition Files (*.6rn);;SGI Files (*.sgi *.rgb *.rgba *.bw *.s16);;SoftImage PIC Files (*.si *.pic);;Stamp Files (*.fustamp);;SUN Raster Files (*.ras);;Tar archives (*.tar);;Targa Files (*.tga);;TIFF Files (*.tif *.tiff *.tif3 *.tif16);;Wavefront rla Files (*.rla *.rla16 *.rpf);;Windows Bitmap Files (*.bmp *.dib);;YUV Files (*.yuv *.yuv8)") , None, )#QtGui.QFileDialog.DontUseNativeDialog)
            
            if not fileName:#<------In case user cancels dialog------
                pass
            else:
                for x in itemsSelected:                
                    try:
                        cmds.setAttr(str(x.text(0)+".ptexFile"), str(fileName), type="string")
                    except:
                        cmds.setAttr(str(x.text(0)+".fileTextureName"), str(fileName), type="string")
                self.checkFiles()#<---------Refresh Treewidget------
#-------Search and Replace:   searches for a pattern string and replaces it on files path, or nodes name-------
    def SearchAndReplace(self):
        class PopUp(QtGui.QDialog):
            def __init__(self, parent = None):
                myScriptDir = cmds.internalVar(userScriptDir=True)
                #selfDirectory = os.path.dirname(__file__)
                uiFile= myScriptDir+'popup2.ui'
                QtGui.QApplication.__init__(self, )
                PyQt4.uic.loadUi(uiFile, self)#<-----Loading UI
                self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)#------making the new window frameles, and on top-------
                self.exec_()
#---------Re defining mouse events, required to move a frameless window-------------
            def mousePressEvent(self, event):
                self.offset = event.pos()
                QtGui.QDialog.mousePressEvent(self, event)
            def mouseMoveEvent(self, event):
                x=event.globalX()
                y=event.globalY()
                x_w = self.offset.x()
                y_w = self.offset.y()
                self.move(x-x_w, y-y_w)
                QtGui.QDialog.mousePressEvent(self, event)
#--------Exit: close button---------------
            def Exit(self):
                self.reject()
            def SelectAll(self):
                PyForm.treeWidget.selectAll()
#-----------Snr:   replaces the string in path or in loaders name
            def SnR(self):
                ReplaceIn = (self.replaceInComboBox.currentIndex())
                old = self.SearchForLineEdit.displayText()
                new = self.ReplaceWithLineEdit.displayText()
                itemsSelected = PyForm.treeWidget.selectedItems()
                if ReplaceIn == 0: #---------- in path
                    NodesPaths = []
                    for x in itemsSelected:
                        try:
                            path =  cmds.getAttr(str(x.text(0))+".ptexFile")
                            NodesPaths.append(os.path.abspath(path))
                        except :
                            path =  cmds.getAttr(str(x.text(0))+".fileTextureName")
                            NodesPaths.append(os.path.abspath(path))                     
                    newPaths = []
                    for x in NodesPaths:
                        newPaths.append(os2emxpath.normpath((x.replace(old, new))))
                    for x,y in enumerate(newPaths):
                        try:
                            cmds.setAttr(str(QtGui.QTreeWidgetItem.text(itemsSelected[x],0)+".ptexFile"), y, type="string")
                        except :
                            cmds.setAttr(str(QtGui.QTreeWidgetItem.text(itemsSelected[x],0)+".fileTextureName"), y, type="string")
                    FilesManager.checkFiles(PyForm)
                if ReplaceIn == 1: #-------- in Nodes name
                    NodeNameS = []
                    for x in itemsSelected:
                        NodeNameS.append(str(x.text(0)))
                    NodeNewNameS = []
                    for x in NodeNameS:
                        NodeNewNameS.append(x.replace(old, new))
                    for x,y in enumerate(NodeNameS):
                        cmds.rename (str(y), str(NodeNewNameS[x]))
                    FilesManager.checkFiles(PyForm)#-------update treewidget
        app = PopUp([])
#-------COpy TO: Copy all files to folder------
    def CopyTo(self):
        class CopyToPopUp(QtGui.QDialog):
            def __init__(self, parent = None):
                #selfDirectory = os.path.dirname(__file__)
                myScriptDir = cmds.internalVar(userScriptDir=True)
                uiFile= myScriptDir+'CopyTo.ui'
                QtGui.QApplication.__init__(self, )
                PyQt4.uic.loadUi(uiFile, self)#<-----Loading UI
                self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)#------making the new window frameles, and on top-------
                #self.setWindowOpacity(0.5)
                #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)               
                self.exec_()
#---------Re defining mouse events, required to move a frameless window-------------
            def mousePressEvent(self, event):
                self.offset = event.pos()
                QtGui.QDialog.mousePressEvent(self, event)
            def mouseMoveEvent(self, event):
                x=event.globalX()
                y=event.globalY()
                x_w = self.offset.x()
                y_w = self.offset.y()
                self.move(x-x_w, y-y_w)
                QtGui.QDialog.mousePressEvent(self, event)
#--------Exit: close button---------------
            def Exit(self):
                self.reject()
#---------chooseDir: Path Dialog----------------
            def chooseDir(self):    
                pathDir = QtGui.QFileDialog.getExistingDirectory(self, ("Choose Dir"), "c:", options=QtGui.QFileDialog.ShowDirsOnly )
                #PySide.QtGui.QFileDialog.getExistingDirectory([parent=None[, caption=""[, dir=""[, options=QFileDialog.ShowDirsOnly]]]])
                if not pathDir:
                    pass
                else:
                    self.DstPathLineEdit.setText(pathDir)
                
#-----------Snr:   replaces the string in path or in loaders name
            def CopyToFun(self):
                Dst = self.DstPathLineEdit.displayText()
                import filecmp
                import shutil
                NodesPaths = []
                for x in items:
                    try:
                        path =  cmds.getAttr(str(x.text(0))+".ptexFile")
                        NodesPaths.append(str(os.path.abspath(path)))
                    except :
                        path =  cmds.getAttr(str(x.text(0))+".fileTextureName")
                        NodesPaths.append(str(os.path.abspath(path)))  
                pathstochange = []
                for x in NodesPaths:
                    mount = os.path.splitunc(x)[0]#<------Checks if files are on a network drive, or local drive letter.
                    if not mount:
                        pathstochange.append(x.replace(os.path.splitdrive(x)[0], Dst))
                    else:
                        pathstochange.append(x.replace(os.path.splitunc(x)[0], Dst))                
                for x in pathstochange:
                    try:
                        os.makedirs(os.path.dirname(x))#<------Makes Dir Structure
                    except:
                        pass
                self.CopyProgressBar.setMaximum(len(NodesPaths))#<---------- Sets progress bar maximum with number of files
                for x, y in enumerate(NodesPaths):
                    try:
                        if filecmp.cmp(y, (pathstochange[x])) == False:
                            shutil.copy2(y, os.path.dirname(pathstochange[x]))#<------------ Copy File
                            print "File:"+os.path.basename(y)+"<------Replaced"                          
                        else:
                            print "File:"+os.path.basename(y)+"<------Already Exists, skipping"
                            pass
                    except WindowsError:
			    try:
                        	    shutil.copy2(y, os.path.dirname(pathstochange[x]))
                                    print "File:"+os.path.basename(y)+"<------Copied"
		            except IOError:
			            print "File:"+os.path.basename(y)+"<------Doesn not exist, skipping"
		                    pass
		    self.CopyProgressBar.setValue(x+1)#<------------Signal to progress bar

                        
                checkReplace = self.ReplacePathscheckBox.checkState()
                if checkReplace ==2:#<---------Also replace paths in scene, otherwise just copy the files.                
                    for x,y in enumerate(pathstochange):
                        try:
                            cmds.setAttr(str(QtGui.QTreeWidgetItem.text(items[x],0)+".ptexFile"), os2emxpath.normpath(y), type="string")
                        except :
                            cmds.setAttr(str(QtGui.QTreeWidgetItem.text(items[x],0)+".fileTextureName"), os2emxpath.normpath(y), type="string")
                FilesManager.checkFiles(PyForm)
                self.Exit()                
        app = CopyToPopUp([])                      
def main():
    global PyForm
    PyForm=FilesManager()
    PyForm.show()
    
if __name__=="__main__":
    main()
