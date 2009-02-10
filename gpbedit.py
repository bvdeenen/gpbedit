#!/usr/bin/env python
# vim:tw=120

import sys
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
	def __init__(self, field_desc, parent=None):
		QTreeWidgetItem.__init__(self,parent)
		self.field_desc = field_desc
		self.set_column_data()

	def set_column_data(self):

		container = self.parent().gpbitem
		fd=self.field_desc
		t = fd.type

		if t == FD.STRING:
			default_value=fd.default_value
			value = getattr(container, fd.name)
		elif t==FD.ENUM:
			value = getattr(container, fd.name)
			value=fd.enum_type.values_by_number[value].name
			default_choice=fd.default_value
			default_value = fd.enum_type.values_by_number[default_choice].name
		else:	
			default_value=unicode(fd.default_value)
			value = unicode(getattr(container, fd.name))

		self.setText(0, fd.name)
		self.setText(1, str(t))
		self.setText(2, FD.type_map[t].lower())
		self.setText(3, FD.label_map[fd.label].lower())
		self.setText(4,default_value)
		self.setText(5, value)

class MessageTreeItem(QTreeWidgetItem):

	def __init__(self, field_desc, gpbitem, parent=None):
		QTreeWidgetItem.__init__(self,parent)

		self.setExpanded(True)
		self.field_desc = field_desc
		self.gpbitem = gpbitem
		self.createFieldCategories()

		if not field_desc:  # for the top level
			self.setText(0,gpbitem.DESCRIPTOR.name)
		else: 
			labels=[field_desc.name, "", gpbitem.DESCRIPTOR.name ,FD.label_map[field_desc.label].lower()]
			for i,l in enumerate(labels): self.setText(i,str(l))

		ct=self.createRequiredFieldItems()

		for field_desc, object in self.gpbitem.ListFields():
			if field_desc.type== FD.MESSAGE:
				if field_desc.label == FD.REPEATED: 
					for fi in object:
						MessageTreeItem(field_desc, fi, self)
				else: # required or optional
					MessageTreeItem(field_desc, object, self)
			else: # its a non-message field
				if field_desc.label == FD.REPEATED: 
					for fi in object:
						FieldTreeItem(field_desc, self)
				else: # optional or required
					FieldTreeItem(field_desc, self)
		self.createRequiredMessageItems()			

	
	def createRequiredFieldItems(self):
		i=0
		for fieldname, fd in self.required_fields.items():
			if self.gpbitem.HasField(fd.name): continue # it's already defined
			if fd.type == FD.MESSAGE :  continue # only fields

			# create a field when it is required and not yet existing
			# the FieldTreeItem is created from the MessageTreeItem constructor
			i+=1
			setattr(self.gpbitem, fd.name, fd.default_value)
		return i			

	def createRequiredMessageItems(self):
		i=0
		for fieldname, fd in self.required_fields.items():
			if self.gpbitem.HasField(fd.name): continue # it's already defined
			if fd.type != FD.MESSAGE : continue # only message items
			self.createNestedMessage(fieldname)
			i+=1
		return i			

	def add_gpb_child(self, fd):
		if fd.type == FD.MESSAGE:
			child = self.createNestedMessage(fd.name)
		else:	
			child = FieldTreeItem(fd, self)
		self.treeWidget().setCurrentItem(child)
		self.treeWidget().emit( SIGNAL("itemClicked(QTreeWidgetItem*, int)"), child,0)
		
	def createNestedMessage(self, fieldname):
		fd= self.gpbitem.DESCRIPTOR.fields_by_name[fieldname]

		if fd.type==FD.MESSAGE : # message
			if fd.label==FD.REPEATED : # repeated
				o = getattr(self.gpbitem, fieldname)
				gpbmessage = o.add()
				child = MessageTreeItem(fd, gpbmessage, self)
			else: # optional or required
				o = getattr(self.gpbitem, fieldname)
				child = MessageTreeItem(fd, o, self)
				
		self.treeWidget().emit_gpbupdate()		
		return child
	

				


	def createFieldCategories(self):
		""" create the tree dictionaries with fields of this message type
		"""
		self.required_fields={}
		self.optional_fields={}
		self.repeated_fields={}
		for fieldname, fd in self.gpbitem.DESCRIPTOR.fields_by_name.items():
			if fd.label == FD.OPTIONAL : 
				self.optional_fields[fieldname] = fd
			elif fd.label ==FD.REQUIRED : 
				self.required_fields[fieldname] = fd
			elif fd.label==FD.REPEATED: 
				self.repeated_fields[fieldname] = fd
			else:
				print "unknown label"
				sys.exit(1)

		
class TreeWidget(QTreeWidget):
	""" The container tree for all the gpb objects that we have created/destroyed
	"""
	def __init__(self, parent=None):
		QTreeWidget.__init__(self, parent)
		self.filename = ""
	def emit_gpbupdate(self):
		""" our gpb object(s) have changed
		"""
		self.emit(SIGNAL("gpbobject_updated(PyQt_PyObject)"), self.topLevelItem(0))

	def save_gpb(self):
		filename = QFileDialog.getSaveFileName(self, "save gpb file", self.filename)
		if not filename : return
		self.filename=filename

		f=open(filename,"wb")
		f.write(self.topLevelItem(0).gpbitem.SerializeToString())
		f.close()

	def open_gpb(self):
		filename = QFileDialog.getOpenFileName(self, "open gpb file", self.filename, "GPB files (*.gpb);;All files (*.*)")
		if not filename: return
		self.loadfile(filename)

	def loadfile(self,filename):
		self.clear_gpb()
		self.filename=filename
		f=open(filename,"rb")
		gpb=settings.empty_root_message()
		gpb.ParseFromString( f.read())
		f.close()
		self.create_toplevel(gpb)
		# top=MessageTreeItem(None, gpb)
		# self.addTopLevelItem(top)
		# self.expandItem(top)
		# self.emit_gpbupdate()


	def clear_gpb(self):
		global editwidget
		editwidget.no_edit()
		c= self.topLevelItem(0)
		del c
		self.invisibleRootItem().removeChild( self.topLevelItem(0))
	
	def create_toplevel(self, gpb=None):
		if not gpb:
			gpb=settings.empty_root_message()
		top=MessageTreeItem(None, gpb)
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
	
	gpb_top = MessageTreeItem( None, settings.empty_root_message())
	treewidget.addTopLevelItem(gpb_top)

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



	QObject.connect( treewidget, SIGNAL("gpbobject_updated(PyQt_PyObject)"),
		debugwidget.slot_gpbobject_updated)

	QObject.connect(savebutton, SIGNAL("clicked()"), treewidget.save_gpb)	
	QObject.connect(openbutton, SIGNAL("clicked()"), treewidget.open_gpb)	
	QObject.connect(clearbutton, SIGNAL("clicked()"), treewidget.start_with_empty_toplevel)	

	editwidget.make_connections(treewidget)

	treewidget.expandItem(gpb_top)
	treewidget.setColumnWidth(0,220)
	treewidget.setColumnWidth(1,60)
	mainwindow.setMinimumSize(QSize(1000,800))

	mainwindow.show()

	#if settings.loadfile: treewidget.loadfile(settings.loadfile)
		
	treewidget.emit_gpbupdate()


	sys.exit(app.exec_())
