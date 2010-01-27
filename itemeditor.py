#!/usr/bin/env python
# vim:tw=120
# -*- coding: utf-8 -*-

## @package itemeditor generic type of item editor, using EnumEditor, ValueEditor and BooleanEditor to do the work.
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import __main__ 

from valueeditor import *
from messageeditor import *
from enumeditor import *
from booleaneditor import *

import FD

## widget that contains three different kinds of editors (EnumEditor, ValueEditor and BooleanEditor), and that shows
# only one depending on the type of treewidget that gets editted.
class ItemEditor(QWidget):

	## constructor.
	def __init__(self, parent=None):

		## @var stack
		# QStackedWidget that has the three editors

		## @var blankeditor
		# 'editor' that shows nothing.

		## @var enumeditor
		# editor shown when editting enums

		## @var booleaneditor
		# editor shown when editting booleans

		## @var valueeditor
		# editor shown when editting textual (or numeric) values


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

			
	

