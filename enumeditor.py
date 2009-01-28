# vim:tw=120
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

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

		QObject.connect(self.enumpopup, SIGNAL("triggered(QAction *)"),
			self.pick_enum)

		vbox.addStretch()
	
	def set_treewidget(self, widgetitem):

		self.widgetitem = widgetitem
		self.fd = widgetitem.field_desc

		self.namelabel.setText(self.fd.name)
		self.enumtypelabel.setText(self.fd.enum_type.name)
		self.enumpopup.clear()

		for key,value in self.fd.enum_type.values_by_number.items():
			action = self.enumpopup.addAction("%d %s" %( value.number, value.name))
			if  key == self.fd.default_value :
				self.enumpopup.setActiveAction( action)
	
	def pick_enum(self, action):
		n,name = str(action.text()).split(None,1)

		container = self.widgetitem.parent().gpbitem
		setattr(container, self.fd.name, int(n))

		self.widgetitem.set_column_data()
		self.widgetitem.treeWidget().emit_gpbupdate()

