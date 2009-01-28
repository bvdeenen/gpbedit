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

		vbox.addStretch()
	
	def set_treewidget(self, widgetitem):

		fd = widgetitem.field_desc
		container = widgetitem.parent().gpbitem
		descriptor=container.DESCRIPTOR

		self.namelabel.setText(fd.name)
		self.enumtypelabel.setText(descriptor.enum_type.name)
		self.enumpopup.clear()

		for key,value in descriptor.enum_type.values_by_number.items():
			action = self.enumpopup.addAction("%d %s" %( value.number, value.name))
			if  key == descriptor.default_value :
				self.enumpopup.setActiveAction( action)

