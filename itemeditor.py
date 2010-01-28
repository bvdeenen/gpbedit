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

		self.deletebutton=QPushButton(self)
		self.deletebutton.setText("&Delete")
		vbox.addWidget(self.deletebutton)
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
		self.deletebutton.hide()

	def make_connections(self, treewidget):
		QObject.connect(treewidget, 
			SIGNAL('itemClicked ( QTreeWidgetItem *, int )'),
			self.slot_treeitem_click)
		QObject.connect(treewidget, 
			SIGNAL('itemActivated ( QTreeWidgetItem *, int )'),
			self.slot_treeitem_click)

		QObject.connect(self.deletebutton, 
			SIGNAL('clicked()'),
			self.slot_do_delete)

	def slot_do_delete(self):
		treewidget = self.widgetitem.treeWidget()
		self.widgetitem.parent().removeChild(self.widgetitem)
		del self.widgetitem
		self.no_edit()
		ci = treewidget.currentItem()
		if ci : 
			self.slot_treeitem_click(ci)
		treewidget.emit_gpbupdate()
	
	def slot_treeitem_click(self, widgetitem, column=0):
		fd = widgetitem.field_desc
		self.widgetitem = widgetitem

		fieldname = widgetitem.text(0)


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

	
		p = widgetitem.parent()

		label = -1
		if p :
			if type(widgetitem) == __main__.MessageTreeItem and widgetitem.field :
				label = widgetitem.field.label
			else:	
				label= widgetitem.field_desc.label
		self.deletebutton.setVisible( label==FD.REPEATED or label==FD.OPTIONAL)	
			
	

