# vim:tw=120
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import FD

class BooleanEditor(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		label=QLabel(self)
		label.setText("BooleanEditor")
		vbox.addWidget(label)

		self.namelabel=QLabel(self)
		vbox.addWidget(self.namelabel)

		self.typelabel=QLabel(self)
		vbox.addWidget(self.typelabel)

		self.checkbox=QCheckBox(self)
		vbox.addWidget(self.checkbox)
		vbox.addStretch()
	
		QObject.connect(self.checkbox, SIGNAL("stateChanged(int)"),
			self.editFinished)

	def set_treewidget(self, widgetitem):
		self.widgetitem = widgetitem
		fd = widgetitem.field_desc
		container = widgetitem.parent().gpbitem
		descriptor=container.DESCRIPTOR
		self.fd = fd
		self.container= container

		t=FD.type_map[self.fd.type]
		self.typelabel.setText(t)

		self.namelabel.setText(fd.name)

		value = getattr(self.container, self.fd.name)
		if value :
			self.checkbox.setCheckState( Qt.Checked)
		else:	
			self.checkbox.setCheckState( Qt.Unchecked)

		
		self.checkbox.setFocus()	

	def editFinished(self, state) :
		v = self.checkbox.checkState()
		if v : v=1
		setattr(self.container, self.fd.name, v)


		self.widgetitem.set_column_data()
		self.widgetitem.treeWidget().emit_gpbupdate()




