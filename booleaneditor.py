# vim:tw=120
# -*- coding: utf-8 -*-

## @package booleaneditor
# Boolean editor.

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import FD

## @brief checkbox editor for editting boolean values.
class BooleanEditor(QWidget):
	## @var namelabel
	# the QLabel that gets the name of this field.
	# typical values: antialias, synchronous, last, parent_width, ...

	## @var typelabel
	# the QLabel that gets the type of this field ('BOOL')

	## @var checkbox
	# the QCheckBox that holds the boolean value.

	## @var widgetitem
	# the widgetitem that we're editting with this EnumEditor.

	## constructor.
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

	## connect tree widget to this BooleanEditor.
	def set_treewidget(self, widgetitem):
		self.widgetitem = widgetitem
		fd = widgetitem.field_desc

		self.typelabel.setText(FD.type_map[fd.type])
		self.namelabel.setText(fd.name)

		if widgetitem.get_value() :
			self.checkbox.setCheckState( Qt.Checked)
		else:	
			self.checkbox.setCheckState( Qt.Unchecked)

		self.checkbox.setFocus()	

	## slot that gets called when the checkbox changes value.
	# @param state unused
	def editFinished(self, state) :
		v = self.checkbox.checkState()
		if v : v=1
		self.widgetitem.set_value(v)
		self.widgetitem.treeWidget().emit_gpbupdate()




