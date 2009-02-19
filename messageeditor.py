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
			self.add_gpb_child)

		gridrow+=1
		grid.addWidget(QLabel("Optional"), gridrow, 0)
		self.optionalpopup=QMenu(self)
		self.optionalmenubutton = QPushButton(self)
		self.optionalmenubutton.setMenu(self.optionalpopup)
		grid.addWidget(self.optionalmenubutton, gridrow,1)

		QObject.connect(self.optionalpopup, SIGNAL("triggered(QAction *)"),
			self.add_gpb_child)

		gridrow+=1
		grid.addWidget(QLabel("Remove object"), gridrow, 0)
		self.deletebutton = QPushButton(self)
		self.deletebutton.setText("Delete")
		grid.addWidget(self.deletebutton, gridrow, 1)

		QObject.connect(self.deletebutton, SIGNAL("clicked()"),
			self.remove_message)

		vbox.addStretch()

	def add_gpb_child(self, action):
		field_name = str(action.text())

		print "self.widgetitem=",self.widgetitem
		container = self.widgetitem.gpbitem
		print field_name, "container=",container
		
		fd = container.DESCRIPTOR.fields_by_name[field_name]
		self.widgetitem.add_gpb_child(fd)
	
	def remove_message(self):
		parent = self.widgetitem.parent()
		parent.removeChild(self.widgetitem)
		container = parent.gpbitem
		container.ClearField(self.widgetitem.gpbitem)
		del self.widgetitem
		self.emit( SIGNAL("closeMe()"))
		
	def set_treewidget(self, widgetitem):
		self.widgetitem=widgetitem
		container = self.widgetitem.gpbitem
		if widgetitem.field_desc:
			self.fd = widgetitem.field_desc
			self.namelabel.setText(widgetitem.field_desc.name)
		else:	
			self.fd = None
			self.namelabel.setText("no parent")

		self.unfilled_optional_fields={}

		for name,fd in  widgetitem.optional_fields.items():
			if not container.HasField(name):
				self.unfilled_optional_fields[name]=fd
			
		self.set_popup_menu(self.repeatedpopup, widgetitem.repeated_fields)
		self.set_popup_menu(self.optionalpopup, self.unfilled_optional_fields)

		self.deletebutton.setEnabled( self.widgetitem.parent()!=None )
	
	
	def set_popup_menu(self, menu, dict) :
		menu.clear()
		for name,fd in dict.items():
			menu.addAction(name)

		




