#!/usr/bin/env python
# vim:tw=120
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from example_pb2 import *
from effects_pb2 import *
from rows_pb2 import *
from google.protobuf import text_format

import __main__ 
from valueeditor import *
from messageeditor import *
from enumeditor import *

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
			
	

