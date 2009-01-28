#!/usr/bin/env python
# vim:tw=120

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import example_pb2 
import effects_pb2
import rows_pb2 

from debugwidget import *
from itemeditor import *

import google
import FD

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
			default_value=fd.default_value.decode('utf-8')
			value = getattr(container, fd.name).decode('utf-8')
		elif t==FD.ENUM:
			value = getattr(container, fd.name)
			value=fd.enum_type.values_by_number[value].name.decode('utf-8')
			default_choice=fd.default_value
			default_value = fd.enum_type.values_by_number[default_choice].name
		else:	
			default_value=unicode(fd.default_value)
			value = unicode(getattr(container, fd.name))

		self.setText(0, fd.name)
		self.setText(1, str(t))
		self.setText(2, FD.type_map[t])
		self.setText(3, FD.label_map[fd.label])
		self.setText(4,default_value)
		self.setText(5, value)

class MessageTreeItem(QTreeWidgetItem):

	def __init__(self, field_desc, gpbitem, parent=None):
		QTreeWidgetItem.__init__(self,parent)

		self.setExpanded(True)
		self.field_desc = field_desc
		self.gpbitem = gpbitem
		self.createFieldCategories()

		self.createRequiredFields()

		if not field_desc:  # for the top level
			self.setText(0,gpbitem.DESCRIPTOR.name)
		else: 
			labels=[field_desc.name, "", gpbitem.DESCRIPTOR.name ,FD.label_map[field_desc.label]]
			for i,l in enumerate(labels): self.setText(i,str(l))

		for field_desc, object in gpbitem.ListFields():
			if field_desc.type== FD.MESSAGE:
				if field_desc.label == FD.REPEATED: 
					for fi in object:
						MessageTreeItem(field_desc, fi, self)
				else: # single
					MessageTreeItem(field_desc, object, self)
			else:
				FieldTreeItem(field_desc, self)
	
	def add_gpb_child(self, fd):
		if fd.type == FD.MESSAGE:
			self.createNestedMessage(fd.name)
		else:	
			FieldTreeItem(fd, self)
		

	def createNestedMessage(self, fieldname):
		fd= self.gpbitem.DESCRIPTOR.fields_by_name[fieldname]

		if fd.type==FD.MESSAGE : # message
			if fd.label==FD.REPEATED : # repeated
				o = getattr(self.gpbitem, fieldname)
				gpbmessage = o.add()
				MessageTreeItem(fd, gpbmessage, self)
			else: # optional or required
				o = getattr(self.gpbitem, fieldname)
				MessageTreeItem(fd, o, self)
				
		self.treeWidget().emit_gpbupdate()		
	
	def createRequiredFields(self):
		for fieldname, fd in self.required_fields.items():
			if fd.label != FD.REQUIRED : continue 
			if self.gpbitem.HasField(fd.name): continue # it's already defined
			if fd.type == FD.MESSAGE : 
				self.createNestedMessage(fieldname)
			else: # non-message type
				FieldTreeItem(fd, self)
				


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
	def emit_gpbupdate(self):
		""" our gpb object(s) have changed
		"""
		self.emit(SIGNAL("gpbobject_updated(PyQt_PyObject)"), self.topLevelItem(0))


if __name__ == "__main__":
	FD.init()
	app = QApplication(sys.argv)
	mainwindow=QWidget()
	layout = QHBoxLayout(mainwindow)
	mainwindow.setLayout(layout)


	treewidget = TreeWidget()
	treewidget.setWindowTitle("Google Protocol Object Editor")
	treewidget.setHeaderLabels( [ "Name" ,"Type" ,"Kind" ,"Label" ,"Default", "Value"])

	message=example_pb2.ILNMessage()

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

	treewidget.expandItem(gpb_top)
	treewidget.setColumnWidth(0,220)
	treewidget.setColumnWidth(1,60)
	mainwindow.setMinimumSize(QSize(1000,800))

	mainwindow.show()

	# some more test message stuff
	gpb_top.createNestedMessage('texts')
	gpb_top.createNestedMessage('rsss')
	gpb_top.createNestedMessage('datasheets')
	gpb_top.createNestedMessage('rsss')



	message.rsss[0].text.frame.object.id="hallo"
	message.rsss[0].text.font="Arial"
	treewidget.emit_gpbupdate()


	sys.exit(app.exec_())
