#!/usr/bin/env python
# vim:tw=120

import sys
import SocketServer
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from debugwidget import *
from itemeditor import *

import google
import FD
import settings

class FieldTreeItem(QTreeWidgetItem):
	""" for tree items that represent a non-message field of a message object
	"""
	def __init__(self, field_desc, value= None, parent=None):
		QTreeWidgetItem.__init__(self,parent, 2001)
		self.field_desc = field_desc
		if value != None:
			self.set_value(value)
		else:
			if field_desc.label == FD.REPEATED:
				self.set_value(None)
			else:
				self.set_value(field_desc.default_value)

	def get_value(self): 
		return self._value

	def set_value(self, value):
		self._value=value
		self.set_column_data()

	def set_column_data(self):

		fd=self.field_desc
		t = fd.type
		print fd.type, fd.name, fd.default_value,  self._value

		if t == FD.STRING:
			default_value=fd.default_value
			if fd.label == FD.REPEATED: default_value=""
			if self._value==None :  self._value=""
			self.setText(5,self._value)
		elif t==FD.ENUM:
			if self._value == None: self._value = 0
			self.setText(5,fd.enum_type.values_by_number[self._value].name)
			if fd.label == FD.REPEATED: 
				default_value = fd.enum_type.values_by_number[0].name
			else:
				default_value = fd.enum_type.values_by_number[fd.default_value].name
		else:	
			if fd.label == FD.REPEATED:
				default_value=""
			else:
				default_value=unicode(fd.default_value)
			self.setText(5,unicode(self._value))

		self.setText(0, fd.name)
		self.setText(1, FD.type_map[t].lower())
		self.setText(2, FD.label_map[fd.label].lower())
		self.setText(4,default_value)
		
	def get_fieldname(self):
		return self.field_desc.name

class MessageTreeItem(QTreeWidgetItem):

	def __init__(self, field_desc, field=None, gpbobject = None, parent=None):
		QTreeWidgetItem.__init__(self,parent, 2000)


		self.setExpanded(True)
		self.field_desc = field_desc
		self.gpbobject = gpbobject
		self.field=field

		self.createFieldCategories()
		if field :
			self.setText(0,field.name)
			self.setText(2,FD.label_map[field.label].lower())
		else:	
			self.setText(0,"^^^")

			
		self.setText(1,self.field_desc.name)

		if self.gpbobject:
			# we're constructing this object from an existing gpb object
			for field, o in self.gpbobject.ListFields():
				if field.type == FD.MESSAGE :  
					if field.label==FD.REPEATED :
						for i in range(len(o)):
							o1=getattr(self.gpbobject,field.name)[i]
							MessageTreeItem (field.message_type, field, o1, self)
					else:		
						o1=getattr(self.gpbobject,field.name)
						MessageTreeItem (field.message_type, field, o1, self)
				else:
					if field.label == FD.REPEATED:
						for i in range(len(o)):
							o1=getattr(self.gpbobject, field.name)[i]
							FieldTreeItem(field, o1, self)
					else:
						FieldTreeItem(field, o, self)
		else:
			# we're constructing a brand new object, with default data
			self.setExpanded(True)
			for fieldname, field_desc in self.required_fields.items():
				if field_desc.type == FD.MESSAGE :  
					MessageTreeItem(field_desc.message_type, field_desc, None, self)
				else:	
					FieldTreeItem(field_desc, None, self)

	def get_fieldname(self):
		if not self.field : return None
		return self.field.name

	def createFieldCategories(self):
		""" create the tree dictionaries with fields of this message type
		"""
		self.required_fields={}
		self.optional_fields={}
		self.repeated_fields={}
		for fieldname, fd in self.field_desc.fields_by_name.items():
			if fd.label == FD.OPTIONAL : 
				self.optional_fields[fieldname] = fd
			elif fd.label ==FD.REQUIRED : 
				self.required_fields[fieldname] = fd
			elif fd.label==FD.REPEATED: 
				self.repeated_fields[fieldname] = fd
			else:
				print "unknown label"
				sys.exit(1)

	def add_child(self, fieldname):
		preceding = self.find_children_by_name(fieldname)
		if preceding: preceding=preceding[-1] # last child
		fd=self.field_desc.fields_by_name[fieldname]

		print "fd=",fd, fd.default_value
		if fd.type == FD.MESSAGE :  
			c=MessageTreeItem(fd.message_type, fd, None, self)
		else:	
			c=FieldTreeItem(fd, None, self)
		
		self.move_child(c, preceding)


		
	def move_child(self, child, precedingchild):
		if not child.parent() : return
		p=child.parent()
		if not precedingchild: 
			# very first
			p.removeChild(child)
			p.insertChild(0,child)
		else:	
			i = p.indexOfChild(precedingchild)
			p.removeChild(child)
			p.insertChild(i+1,child)
		child.treeWidget().setCurrentItem(child)	
		self.treeWidget().emit_gpbupdate()

	def find_same_type_siblings(self):
		if not self.parent() : 
			return []
		return self.parent().find_children_by_name( self.field.name) 

	def move_by_one_enabled(self,dir):
		s = self.find_same_type_siblings()
		if not s or len(s)==1: 
			return None
		i=s.index(self)
		if (i==0 and dir == -1) or (i==len(s)-1 and dir==+1) :
			return None
		return s
		
	def move_by_one(self, dir):
		s = self.move_by_one_enabled(dir)
		if not s: return
		p=self.parent()
		i=s.index(self)
		p.removeChild(self)
		p.insertChild(i+dir,self)
		self.treeWidget().setCurrentItem(self)	
		self.treeWidget().emit_gpbupdate()


	def find_children_by_name(self,name):
		children=[]
		for i in xrange(self.childCount()):
			c=self.child(i)
			if c.get_fieldname() == name :
				children.append(c)
		#print "find_children_by_name(",name,")=",children			
		return children
		

	def find_child_by_name(self,name):
		for i in xrange(self.childCount()):
			c=self.child(i)
			if c.get_fieldname() == name :
				return c
		return None

		
class TreeWidget(QTreeWidget):
	""" The container tree for all the gpb objects that we have created/destroyed
	"""
	def __init__(self, parent=None):
		QTreeWidget.__init__(self, parent)
		self.filename = ""

	def emit_gpbupdate(self):
		""" our gpb object(s) have changed
		"""
		self.emit(SIGNAL("gpbobject_updated(PyQt_PyObject)"), self)

	def save_gpb(self):

		o=settings.new_gpb_root()
		topmessage=self.topLevelItem(0)
		buildgpb.Builder( o, topmessage )

		if not o.IsInitialized() : 
			msgBox = QMessageBox()
			msgBox.setText("The GPB Object tree is incomplete. This is a bug, The file can not be saved")
			msgBox._exec()
			return


		filename = QFileDialog.getSaveFileName(self, "save gpb file", self.filename)
		if not filename : return
		self.filename=filename

		
		f=open(filename,"w")
		f.write( text_format.MessageToString(o))
		f.close()

	def serverpush(self):
		o=settings.new_gpb_root()
		topmessage=self.topLevelItem(0)
		buildgpb.Builder( o, topmessage )

		if not o.IsInitialized() : 
			print "gpb incomplete"
			return
		
		
	def open_gpb(self):
		filename = QFileDialog.getOpenFileName(self, "open gpb file", self.filename, "GPB files (*.gpb);;All files (*.*)")
		if not filename: return
		self.loadfile(filename)

	def loadfile(self,filename):
		self.clear_gpb()
		self.filename=filename
		f=open(filename, "r")
		gpb=settings.new_gpb_root()
		text_format.Merge( f.read(), gpb)
		f.close()

		self.create_toplevel(gpb)


	def clear_gpb(self):
		global editwidget
		editwidget.no_edit()
		#c= self.topLevelItem(0)
		self.invisibleRootItem().removeChild( self.topLevelItem(0))
	
	def create_toplevel(self, gpb=None):
		top=MessageTreeItem(settings.gpb_root_descriptor(), None, gpb)
		self.addTopLevelItem(top)
		self.expandItem(top)
		self.emit_gpbupdate()
	
	def start_with_empty_toplevel(self):
		self.clear_gpb()
		self.create_toplevel()

	


if __name__ == "__main__":
	FD.init()
	app = QApplication(sys.argv)
	mainwindow=QWidget()
	layout = QHBoxLayout(mainwindow)
	mainwindow.setLayout(layout)


	treewidget = TreeWidget()
	treewidget.setWindowTitle("Google Protocol Object Editor")
	treewidget.setHeaderLabels( [ "Name" ,"Type" ,"Kind" ,"Label" ,"Default", "Value"])

	settings.read_settings_file()
	
	treewidget.create_toplevel()

	layout.addWidget(treewidget, 1)

	global editwidget
	editwidget = ItemEditor(mainwindow)

	rightvbox=QVBoxLayout()
	layout.addLayout(rightvbox)
	rightvbox.addWidget(editwidget)
	rightvbox.addStretch()

	debugwidget = DebugWidget(mainwindow)
	debugwidget.setMinimumSize(200,400)
	debugwidget.setMaximumWidth(300)

	rightvbox.addWidget(debugwidget)

	clearbutton=QPushButton("&clear whole tree", mainwindow)
	rightvbox.addWidget(clearbutton)

	savebutton=QPushButton("&save gpb file", mainwindow)
	rightvbox.addWidget(savebutton)

	openbutton=QPushButton("&open gpb file", mainwindow)
	rightvbox.addWidget(openbutton)

	serverpush=QPushButton("&tcp push ", mainwindow)
	rightvbox.addWidget(serverpush)


	QObject.connect( treewidget, SIGNAL("gpbobject_updated(PyQt_PyObject)"), debugwidget.slot_gpbobject_updated)

	QObject.connect(savebutton, SIGNAL("clicked()"), treewidget.save_gpb)	
	QObject.connect(openbutton, SIGNAL("clicked()"), treewidget.open_gpb)	
	QObject.connect(clearbutton, SIGNAL("clicked()"), treewidget.start_with_empty_toplevel)	
	QObject.connect(serverpush, SIGNAL("clicked()"), treewidget.serverpush)	

	editwidget.make_connections(treewidget)

	treewidget.setColumnWidth(0,220)
	treewidget.setColumnWidth(1,60)
	mainwindow.setMinimumSize(QSize(1000,800))

	mainwindow.show()

	if settings.loadfile: treewidget.loadfile(settings.loadfile)
		
	treewidget.emit_gpbupdate()


	sys.exit(app.exec_())
