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
		itemdata=widgetitem.itemData
		self.namelabel.setText(itemdata.name)
		self.enumtypelabel.setText(itemdata.enum_type.name)

		self.enumpopup.clear()

		for key,value in itemdata.enum_type.values_by_number.items():
			action = self.enumpopup.addAction("%d %s" %( value.number, value.name))
			if  key == itemdata.default_value :
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
	
	def set_treewidget(self, widgetitem):
		global type_map
		itemdata=widgetitem.itemData
		self.namelabel.setText(itemdata.name)
		self.typelabel.setText(type_map[itemdata.type])


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


	def okbuttonclicked(self):
		print "klik"

	def make_connections(self, treewidget):
		QObject.connect(treewidget, 
			SIGNAL('itemClicked ( QTreeWidgetItem *, int )'),
			self.slot_treeitem_click)

	
	def slot_treeitem_click(self, widgetitem, column):
		global type_map, label_map
		if type(widgetitem) == __main__.FieldTreeItem :
			# edit a simple type
			fd = widgetitem.field_desc
			container = widgetitem.parent().gpbitem
			value=getattr(container,fd.name)
			print "simple type" , __main__.type_map[fd.type]
			print "container=",type(container), "value=",value
			setattr(container, fd.name, value+1)

			widgetitem.set_column_data()
			widgetitem.treeWidget().emit_gpbupdate()		

			

		elif type(widgetitem) == __main__.MessageTreeItem :
			pass

		#	# it's a message type
		#	self.enumeditor.set_treewidget(widgetitem)
		#	self.stack.setCurrentIndex(0)

		#
		#elif not itemdata.DESCRIPTOR.message_type:
		#	self.valueeditor.set_treewidget(widgetitem)
		#	self.stack.setCurrentIndex(1)
			
	

