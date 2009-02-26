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

		self.enumpopup=QComboBox(self)

		vbox.addWidget(self.enumpopup)

		QObject.connect(self.enumpopup, SIGNAL("currentIndexChanged(int)"),
			self.pick_enum)

		vbox.addStretch()
	
	def set_treewidget(self, widgetitem):

		# so that the 'clear()' call does not generate an update in the widgetitem
		self.widgetitem=None 

		self.enumpopup.clear()
		fd = widgetitem.field_desc

		self.namelabel.setText(fd.name)
		self.enumtypelabel.setText(fd.enum_type.name)

		for key,value in fd.enum_type.values_by_number.items():
			self.enumpopup.addItem("%d %s" %( value.number, value.name))
			if  value.number == widgetitem.get_value():
				self.enumpopup.setCurrentIndex(key)
	
		# only now connect the widgetitem
		self.widgetitem = widgetitem

	def pick_enum(self, index):
		if index<0 or not self.widgetitem: return # don't care about these messages
		v = self.widgetitem.field_desc.enum_type.values_by_number[index]
		self.widgetitem.set_value( v.number)
		self.widgetitem.treeWidget().emit_gpbupdate()

