#!/usr/bin/env python
# vim:tw=120
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import __main__ 

from valueeditor import *
from messageeditor import *
from enumeditor import *
from booleaneditor import *

import FD

class ItemEditor(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)

		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		self.stack = QStackedWidget(self)

		vbox.addWidget(self.stack)
		vbox.addStretch()


		self.blankeditor = QLabel(self)
		self.stack.addWidget(self.blankeditor)

		self.enumeditor=EnumEditor(self.stack)
		self.stack.addWidget(self.enumeditor)

		self.valueeditor=ValueEditor(self.stack)
		self.stack.addWidget(self.valueeditor)

		self.messageeditor=MessageEditor(self.stack)
		self.stack.addWidget(self.messageeditor)

		self.booleaneditor=BooleanEditor(self.stack)
		self.stack.addWidget(self.booleaneditor)

		QObject.connect( self.messageeditor, SIGNAL("closeMe()"),
			self.no_edit)


	def no_edit(self):
		self.stack.setCurrentWidget(self.blankeditor)

	def make_connections(self, treewidget):
		QObject.connect(treewidget, 
			SIGNAL('itemClicked ( QTreeWidgetItem *, int )'),
			self.slot_treeitem_click)
		QObject.connect(treewidget, 
			SIGNAL('itemActivated ( QTreeWidgetItem *, int )'),
			self.slot_treeitem_click)

	
	
	def slot_treeitem_click(self, widgetitem, column):
		fd = widgetitem.field_desc


		if type(widgetitem) == __main__.FieldTreeItem :
			# edit a simple type
			container = widgetitem.parent().gpbitem
			value=getattr(container,fd.name)
			if fd.type == FD.ENUM:
				self.enumeditor.set_treewidget(widgetitem)
				self.stack.setCurrentWidget(self.enumeditor)
			
			elif fd.type == FD.BOOL:
				self.booleaneditor.set_treewidget(widgetitem)
				self.stack.setCurrentWidget(self.booleaneditor)
			
			else:
				widgetitem.set_column_data()
				self.valueeditor.set_treewidget(widgetitem)
				self.stack.setCurrentWidget(self.valueeditor)



		elif type(widgetitem) == __main__.MessageTreeItem :
			self.messageeditor.set_treewidget(widgetitem)
			self.stack.setCurrentWidget(self.messageeditor)

			
	

