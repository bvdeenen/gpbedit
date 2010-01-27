# vim:tw=120
# -*- coding: utf-8 -*-

## @package messageeditor
# item editor for message type items. Shows popups for adding and removing optional and repeated fields.

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import FD


## item editor for message type items. Shows popups for adding and removing optional and repeated fields.
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

		grid = QGridLayout()
		vbox.addLayout(grid)

		gridrow=0
		grid.addWidget(QLabel("Create new child"), gridrow, 0, 1, 2)

		gridrow+=1

		grid.addWidget(QLabel("Repeated"), gridrow, 0)
		self.repeatedpopup=QMenu(self)
		self.repeatedmenubutton = QPushButton(self)
		self.repeatedmenubutton.setMenu(self.repeatedpopup)
		grid.addWidget(self.repeatedmenubutton, gridrow,1)

		QObject.connect(self.repeatedpopup, SIGNAL("triggered(QAction *)"),
			self.add_child)

		gridrow+=1
		grid.addWidget(QLabel("Optional"), gridrow, 0)
		self.optionalpopup=QMenu(self)
		self.optionalmenubutton = QPushButton(self)
		self.optionalmenubutton.setMenu(self.optionalpopup)
		grid.addWidget(self.optionalmenubutton, gridrow,1)

		QObject.connect(self.optionalpopup, SIGNAL("triggered(QAction *)"),
			self.add_child)

		gridrow+=1
		grid.addWidget(QLabel("Remove object"), gridrow, 0)
		self.deletebutton = QPushButton(self)
		self.deletebutton.setText("Delete")
		grid.addWidget(self.deletebutton, gridrow, 1)

		QObject.connect(self.deletebutton, SIGNAL("clicked()"),
			self.remove_message)

		gridrow+=1
		grid.addWidget(QLabel("Move object"), gridrow, 0)
		self.moveup_button = QPushButton(self)
		self.moveup_button.setText("Up")
		self.movedown_button = QPushButton(self)
		self.movedown_button.setText("Down")

		h=QHBoxLayout(self)
		h.addWidget(self.moveup_button)
		h.addWidget(self.movedown_button)
		grid.addLayout(h, gridrow, 1)

		QObject.connect(self.moveup_button, SIGNAL("clicked()"), self.moveup)
		QObject.connect(self.movedown_button, SIGNAL("clicked()"), self.movedown)

		vbox.addStretch()

	def add_child(self, action):
		field_name = str(action.text())

		self.widgetitem.add_child(field_name)
		# remove this menu option if it was one of the optional fields
		for action in self.optionalpopup.actions() :
			if action.text() == field_name:
				self.optionalpopup.removeAction( action) 
		self.widgetitem.treeWidget().emit_gpbupdate()
	
	def remove_message(self):
		treewidget = self.widgetitem.treeWidget()
		self.widgetitem.parent().removeChild(self.widgetitem)
		self.emit( SIGNAL("closeMe()"))
		del self.widgetitem
		treewidget.emit_gpbupdate()
		
	def set_optional_enums(self):	
		unfilled_optional_fields={}
		filled_optional_fields={}
		for name,fd in  self.widgetitem.optional_fields.items():
			if not self.widgetitem.find_child_by_name(name):
				unfilled_optional_fields[name]=fd
		self.set_popup_menu(self.optionalpopup, unfilled_optional_fields)

	def moveup(self):
		self.widgetitem.move_by_one(-1)
		self.set_movebuttons_enable()
		
	def movedown(self):
		self.widgetitem.move_by_one(1)
		self.set_movebuttons_enable()

	def set_treewidget(self, widgetitem):
		self.widgetitem=widgetitem
		self.fd = widgetitem.field_desc
		self.namelabel.setText(widgetitem.field_desc.name)

		self.set_popup_menu(self.repeatedpopup, widgetitem.repeated_fields)
		self.set_optional_enums()


		self.deletebutton.setVisible( self.widgetitem.parent()!=None and self.widgetitem.field != None \
			and self.widgetitem.field.label != FD.REQUIRED )
		self.set_movebuttons_enable()	

	def set_movebuttons_enable(self):
		self.moveup_button.setEnabled( self.widgetitem.move_by_one_enabled(-1)!=None)
		self.movedown_button.setEnabled( self.widgetitem.move_by_one_enabled(1)!=None)
	
	
	def set_popup_menu(self, menu, dict) :
		menu.clear()
		for name,fd in dict.items():
			menu.addAction(name)

		




