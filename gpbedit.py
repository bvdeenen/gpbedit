#!/usr/bin/env python
# vim:tw=120

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from example_pb2 import *
from effects_pb2 import *
from rows_pb2 import *


from debugwidget import *
from itemeditor import *

import google

global type_map, label_map
type_map={}
label_map={}

# return a dictionary with value:name pairs for constants in a field object
# like 
# {1: 'TYPE_DOUBLE', 2: 'TYPE_FLOAT', 3: ...
def create_value_map(object,prefix):
	M={}
	types = [(getattr(object,m),m) for m in dir(object) \
		if not callable(getattr(object,m)) and m.startswith(prefix)]
	for key,value in types:
		M[key]=value
	print M
	return M	


# for tree items that represent a field of a message
class FieldTreeItem(QTreeWidgetItem):
	def __init__(self, field_desc, parent=None):
		QTreeWidgetItem.__init__(self,parent)
		self.field_desc = field_desc
		self.set_column_data()



	def set_column_data(self):
		global type_map, label_map

		typename=type_map[self.field_desc.type]
		container = self.parent().gpbitem

		if typename == "TYPE_STRING" :
			default_value=self.field_desc.default_value.decode('utf-8')
			value = getattr(container, self.field_desc.name).decode('utf-8')
		elif typename=="TYPE_ENUM":
			default_choice=self.field_desc.default_value
			default_value = self.field_desc.enum_type.values_by_number[default_choice].name
			value=self.field_desc.enum_type.values_by_number[value].name.decode('utf-8')
		else:	
			default_value=unicode(self.field_desc.default_value)
			value = unicode(getattr(container, self.field_desc.name))

		labels=[self.field_desc.name, str(self.field_desc.type),typename,label_map[self.field_desc.label], 
			default_value, value]
		for i,l in enumerate(labels): 
			self.setText(i,l)

class MessageTreeItem(QTreeWidgetItem):

	def __init__(self, field_desc, gpbitem, parent=None):
		QTreeWidgetItem.__init__(self,parent)

		self.setExpanded(True)
		self.field_desc = field_desc
		self.gpbitem = gpbitem
		#print "Creating MessageTreeItem", gpbitem.DESCRIPTOR.full_name
		self.createFieldCategories()

		self.createRequiredFields()
		global type_map, label_map

		if not field_desc:  # for the top level
			self.setText(0,gpbitem.DESCRIPTOR.name)
		else: 
			labels=[field_desc.name, "", gpbitem.DESCRIPTOR.name ,label_map[field_desc.label]]
			for i,l in enumerate(labels): self.setText(i,str(l))

		for field_desc, object in gpbitem.ListFields():

			if field_desc.type==11: #message
				if field_desc.label == 3: #repeated
					for fi in object:
						MessageTreeItem(field_desc, fi, self)
				else: # single
					MessageTreeItem(field_desc, object, self)
			else:
				FieldTreeItem(field_desc, self)

	def createNestedMessage(self, fieldname):
		fd= self.gpbitem.DESCRIPTOR.fields_by_name[fieldname]

		if fd.type==11 : # message
			if fd.label==3 : # repeated
				o = getattr(self.gpbitem, fieldname)
				gpbmessage = o.add()
				MessageTreeItem(fd, gpbmessage, self)
			else: # optional or required
				o = getattr(self.gpbitem, fieldname)
				MessageTreeItem(fd, o, self)
				
		self.treeWidget().emit_gpbupdate()		
	
	def createRequiredFields(self):
		for fieldname, fd in self.required_fields.items():
			if fd.label != 2 : continue # not required
			if fd.type == 11 : #message
				self.createNestedMessage(fieldname)
			else: # non-message type
				o=getattr(self.gpbitem, fieldname)
				o=fd.default_value
				FieldTreeItem(fd, self)
				


	def createFieldCategories(self):
		self.required_fields={}
		self.optional_fields={}
		self.repeated_fields={}
		for fieldname, fd in self.gpbitem.DESCRIPTOR.fields_by_name.items():
			if fd.label == 1 : #optional
				self.optional_fields[fieldname] = fd
			elif fd.label ==2 : # required	
				self.required_fields[fieldname] = fd
			elif fd.label==3: #repeated	
				self.repeated_fields[fieldname] = fd
			else:
				print "unknown label"
				sys.exit(1)

		
def setup_maps(gpbitem):
	name,field_desc = gpbitem.DESCRIPTOR.fields_by_name.items()[0]
	global type_map, label_map
	if not type_map: type_map=create_value_map(field_desc,"TYPE_")
	if not label_map: label_map=create_value_map(field_desc,"LABEL_")

class TreeWidget(QTreeWidget):
	def __init__(self, parent=None):
		QTreeWidget.__init__(self, parent)
	def emit_gpbupdate(self):
		self.emit(SIGNAL("gpbobject_updated(PyQt_PyObject)"), self.topLevelItem(0))


if __name__ == "__main__":
	app = QApplication(sys.argv)
	mainwindow=QWidget()
	layout = QHBoxLayout(mainwindow)
	mainwindow.setLayout(layout)


	treewidget = TreeWidget()
	treewidget.setWindowTitle("Simple Tree Model")
	treewidget.setHeaderLabels( [ "Name" ,"Type" ,"Kind" ,"Label" ,"Default", "Value"])

	message=ILNMessage()
	setup_maps(message)

	# obj=message.objects.add()
	# obj.type=123
	# obj.id="bart"

	# rss=message.rsss.add()
	# rss.refreshtime=1.234

	#obj.autohide=5
	#obj.anchor.anchor_id="the anchor id"
	#obj.anchor.anchor=2

	gpb_top = MessageTreeItem( None, message)
	
	treewidget.addTopLevelItem(gpb_top)

	layout.addWidget(treewidget, 1)

	editwidget = ItemEditor(mainwindow)

	rightvbox=QVBoxLayout()
	layout.addLayout(rightvbox)
	rightvbox.addWidget(editwidget)
	rightvbox.addStretch()

	debugwidget = DebugWidget(mainwindow)
	rightvbox.addWidget(debugwidget)

	debugwidget.setMaximumWidth(300)

	QObject.connect( treewidget, SIGNAL("gpbobject_updated(PyQt_PyObject)"),
		debugwidget.slot_gpbobject_updated)

	editwidget.make_connections(treewidget)

	mainwindow.show()
	gpb_top.createNestedMessage('texts')
	gpb_top.createNestedMessage('rsss')
	gpb_top.createNestedMessage('datasheets')
	gpb_top.createNestedMessage('rsss')

	message.rsss[0].text.frame.object.id="hallo"
	message.rsss[0].text.font="Arial"
	treewidget.emit_gpbupdate()

	treewidget.expandItem(gpb_top)

	mainwindow.setMinimumSize(QSize(1000,800))
	sys.exit(app.exec_())
