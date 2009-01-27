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

global type_map, label_map, gpb_top
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
	def __init__(self, field_desc, object, parent=None):
		QTreeWidgetItem.__init__(self,parent)

		global type_map, label_map

		typename=type_map[field_desc.type]
		default_value=field_desc.default_value
		value=object

		if field_desc.enum_type:
			default_value = field_desc.enum_type.values_by_number[default_value].name
			value=field_desc.enum_type.values_by_number[value].name

		labels=[field_desc.name, field_desc.type,typename,label_map[field_desc.label], 
			default_value, value]
		for i,l in enumerate(labels): self.setText(i,str(l))

class MessageTreeItem(QTreeWidgetItem):

	def __init__(self, field_desc, gpbitem, parent=None):
		QTreeWidgetItem.__init__(self,parent)
		self.setExpanded(True)
		self.field_desc = field_desc
		self.gpbitem = gpbitem
		self.createFieldCategories()

		global type_map, label_map

		if not field_desc:  # for the top level
			self.setText(0,gpbitem.DESCRIPTOR.name)
		else: 
			labels=[field_desc.name, "", gpbitem.DESCRIPTOR.name ,label_map[field_desc.label]]
			for i,l in enumerate(labels): self.setText(i,str(l))

		for field_desc, object in gpbitem.ListFields():

			if not type_map: type_map=create_value_map(field_desc,"TYPE_")
			if not label_map: label_map=create_value_map(field_desc,"LABEL_")

			if field_desc.type==11: #message
				if field_desc.label == 3: #repeated
					for fi in object:
						MessageTreeItem(field_desc, fi, self)
				else: # single
					MessageTreeItem(field_desc, object, self)
			else:
				FieldTreeItem(field_desc, object, self)

	def createNestedMessage(self, fieldname):
		fd= self.repeated_fields[fieldname]
		if fd.type==11 : # message
			if fd.label==3 : # repeated
				o = getattr(self.gpbitem, fieldname)
				gpbmessage = o.add()
				MessageTreeItem(fd,gpbmessage, self)
		self.treeWidget().emit_gpbupdate()		
	
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

	obj=message.objects.add()
	obj.type=123
	obj.id="bart"

	rss=message.rsss.add()
	rss.refreshtime=1.234

	obj.autohide=5
	obj.anchor.anchor_id="the anchor id"
	obj.anchor.anchor=2

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


	QObject.connect( treewidget, SIGNAL("gpbobject_updated(PyQt_PyObject)"),
		debugwidget.slot_gpbobject_updated)

	editwidget.make_connections(treewidget)

	mainwindow.show()
	gpb_top.createNestedMessage('texts')

	mainwindow.setMinimumSize(QSize(1000,800))
	sys.exit(app.exec_())
