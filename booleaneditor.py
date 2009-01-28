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

		t=FD.type_map[fd.type]
		self.typelabel.setText(t)

		self.namelabel.setText(fd.name)

		value = getattr(container, fd.name)
		if value :
			self.checkbox.setCheckState( Qt.Checked)
		else:	
			self.checkbox.setCheckState( Qt.Unchecked)

		
		self.checkbox.setFocus()	

	def editFinished(self, state) :
		v = self.checkbox.checkState()
		if v : v=1

		fd = self.widgetitem.field_desc
		container = self.widgetitem.parent().gpbitem
		setattr(container, fd.name, v)

		self.widgetitem.set_column_data()
		self.widgetitem.treeWidget().emit_gpbupdate()




