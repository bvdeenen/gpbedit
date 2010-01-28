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

	## @var form
	# the QFormLayout that holds the various popups.

	## constructor.
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		label=QLabel(self)
		label.setText("MessageEditor")
		vbox.addWidget(label)
		self.namelabel=QLabel(self)
		vbox.addWidget(self.namelabel)

		vbox.addWidget(QLabel("Create new child"))
		self.form = QFormLayout()

		vbox.addLayout(self.form)


		self.repeatedpopup=QMenu(self)
		self.repeatedmenubutton = QPushButton(self)
		self.repeatedmenubutton.setMenu(self.repeatedpopup)
		self.form.addRow("&Repeated", self.repeatedmenubutton)

		QObject.connect(self.repeatedpopup, SIGNAL("triggered(QAction *)"),
			self.add_child)

		self.optionalpopup=QMenu(self)
		self.optionalmenubutton = QPushButton(self)
		self.optionalmenubutton.setMenu(self.optionalpopup)

		self.form.addRow("&Optional",self.optionalmenubutton)

		QObject.connect(self.optionalpopup, SIGNAL("triggered(QAction *)"),
			self.add_child)

		vbox.addStretch()

	def add_child(self, action):
		field_name = str(action.text())

		self.widgetitem.add_child(field_name)
		# remove this menu option if it was one of the optional fields
		for action in self.optionalpopup.actions() :
			if action.text() == field_name:
				self.optionalpopup.removeAction( action) 
		self.widgetitem.treeWidget().emit_gpbupdate()
	
		
	def set_optional_enums(self):	
		unfilled_optional_fields={}
		filled_optional_fields={}
		for name,fd in  self.widgetitem.optional_fields.items():
			if not self.widgetitem.find_child_by_name(name):
				unfilled_optional_fields[name]=fd
		self.set_popup_menu(self.optionalpopup, unfilled_optional_fields)
		self.optionalmenubutton.setEnabled( len(unfilled_optional_fields))


	def set_treewidget(self, widgetitem):
		self.widgetitem=widgetitem
		self.fd = widgetitem.field_desc
		self.namelabel.setText(widgetitem.field_desc.name)

		self.set_popup_menu(self.repeatedpopup, widgetitem.repeated_fields)
		self.repeatedmenubutton.setEnabled(  len(widgetitem.repeated_fields ))
			
			
			
		self.set_optional_enums()


	
	
	def set_popup_menu(self, menu, dict) :
		menu.clear()
		for name,fd in dict.items():
			menu.addAction(name)

		




