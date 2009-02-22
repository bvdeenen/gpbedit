# vim:tw=120
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *


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

		vbox.addStretch()

	def add_child(self, action):
		field_name = str(action.text())

		self.widgetitem.add_child(field_name)
	
	def remove_message(self):
		self.widgetitem.parent().removeChild(self.widgetitem)
		del self.widgetitem
		self.emit( SIGNAL("closeMe()"))
		
	def set_treewidget(self, widgetitem):
		self.widgetitem=widgetitem
		self.fd = widgetitem.field_desc
		self.namelabel.setText(widgetitem.field_desc.name)

		self.unfilled_optional_fields={}

		for name,fd in  widgetitem.optional_fields.items():
			if not widgetitem.find_child_by_name(name):
				self.unfilled_optional_fields[name]=fd
			
		self.set_popup_menu(self.repeatedpopup, widgetitem.repeated_fields)
		self.set_popup_menu(self.optionalpopup, self.unfilled_optional_fields)

		self.deletebutton.setEnabled( self.widgetitem.parent()!=None )

	
	
	def set_popup_menu(self, menu, dict) :
		menu.clear()
		for name,fd in dict.items():
			menu.addAction(name)

		




