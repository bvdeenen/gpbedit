#!/usr/bin/env python
# vim:tw=120
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from example_pb2 import *
from effects_pb2 import *
from rows_pb2 import *
from google.protobuf import text_format

import __main__ 

class MessageEditor(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		label=QLabel(self)
		label.setText("MessageEditor")
		vbox.addWidget(label)
		self.namelabel=QLabel(self)
		vbox.addWidget(self.namelabel)


		vbox.addStretch()
	
	def set_treewidget(self, widgetitem):
		global type_map, label_map

		fd = widgetitem.field_desc
		container = widgetitem.parent().gpbitem

		self.namelabel.setText(fd.name)

class EnumEditor(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		label=QLabel(self)
		label.setText("EnumEditor")
		vbox.addWidget(label)
		self.namelabel=QLabel(self)
		vbox.addWidget(self.namelabel)

		self.enumtypelabel=QLabel(self)
		vbox.addWidget(self.enumtypelabel)

		self.enumpopup=QMenu(self)

		self.menubutton = QPushButton(self)
		self.menubutton.setMenu(self.enumpopup)
		vbox.addWidget(self.menubutton)

		vbox.addStretch()
	
	def set_treewidget(self, widgetitem):
		global type_map, label_map

		fd = widgetitem.field_desc
		container = widgetitem.parent().gpbitem
		descriptor=container.DESCRIPTOR

		self.namelabel.setText(fd.name)
		self.enumtypelabel.setText(descriptor.enum_type.name)
		self.enumpopup.clear()

		for key,value in descriptor.enum_type.values_by_number.items():
			action = self.enumpopup.addAction("%d %s" %( value.number, value.name))
			if  key == descriptor.default_value :
				self.enumpopup.setActiveAction( action)

class ValueEditor(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		label=QLabel(self)
		label.setText("ValueEditor")
		vbox.addWidget(label)

		self.namelabel=QLabel(self)
		vbox.addWidget(self.namelabel)

		self.typelabel=QLabel(self)
		vbox.addWidget(self.typelabel)

		self.editbox=QLineEdit(self)
		vbox.addWidget(self.editbox)
		vbox.addStretch()
	
		QObject.connect(self.editbox, SIGNAL("editingFinished()"),
			self.editFinished)

	def set_treewidget(self, widgetitem):
		self.widgetitem = widgetitem
		fd = widgetitem.field_desc
		container = widgetitem.parent().gpbitem
		descriptor=container.DESCRIPTOR
		self.fd = fd
		self.container= container

		self.namelabel.setText(fd.name)
		self.typelabel.setText(__main__.type_map[fd.type])
		#print getattr(container, fd.name), "****"
		self.editbox.setText( str(getattr(container, fd.name)))

	def editFinished(self) :
		v = self.editbox.text()
		t=__main__.type_map[self.fd.type]

		if  t == "TYPE_STRING" :
			s=""
			s+=v
			setattr(self.container, self.fd.name, s)
		elif t.find("INT") >= 0 :
			setattr(self.container, self.fd.name, int(v))
		else:	
			setattr(self.container, self.fd.name, float(v))
		self.widgetitem.set_column_data()
		self.widgetitem.treeWidget().emit_gpbupdate()



class ItemEditor(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		self.stack = QStackedWidget(self)

		vbox.addWidget(self.stack)
		vbox.addStretch()

		self.okbutton=QPushButton(self)
		self.okbutton.setText("save")

		vbox.addWidget(self.okbutton)
		QObject.connect(self.okbutton,
			SIGNAL('clicked()'),
			self.okbuttonclicked)

		self.enumeditor=EnumEditor(self.stack)
		self.stack.addWidget(self.enumeditor)

		self.valueeditor=ValueEditor(self.stack)
		self.stack.addWidget(self.valueeditor)

		self.messageeditor=MessageEditor(self.stack)
		self.stack.addWidget(self.messageeditor)


	def okbuttonclicked(self):
		print "klik"

	def make_connections(self, treewidget):
		QObject.connect(treewidget, 
			SIGNAL('itemClicked ( QTreeWidgetItem *, int )'),
			self.slot_treeitem_click)

	
	def slot_treeitem_click(self, widgetitem, column):
		global type_map, label_map
		fd = widgetitem.field_desc

		container = widgetitem.parent().gpbitem
		typename = __main__.type_map[fd.type]

		if type(widgetitem) == __main__.FieldTreeItem :
			# edit a simple type
			value=getattr(container,fd.name)
			if fd.type == 14:
				self.enumeditor.set_treewidget(widgetitem)
				self.stack.setCurrentIndex(0)
			
			else:
				widgetitem.set_column_data()
				self.valueeditor.set_treewidget(widgetitem)
				self.stack.setCurrentIndex(1)



		elif type(widgetitem) == __main__.MessageTreeItem :
			self.messageeditor.set_treewidget(widgetitem)
			self.stack.setCurrentIndex(2)

		#
		#elif not itemdata.DESCRIPTOR.message_type:
		#	self.valueeditor.set_treewidget(widgetitem)
		#	self.stack.setCurrentIndex(1)
			
	

