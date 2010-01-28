# vim:tw=120
# -*- coding: utf-8 -*-

## @package valueeditor
# Value editor. @see ValueEditor

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import FD

## editor for entering values (numbers, strings). 
# handles validation for floats, integers, strings.
class ValueEditor(QWidget):

	## @var widgetitem
	# the widget item that gets and sets the value of this ValueEditor.

	## @var namelabel
	# the QLabel that holds the name of the field.
	# Typical values: id, width, ...

	## @var typelabel
	# the QLabel that holds the type of the field 
	# Typical values: STRING, INT32, FLOAT, ...

	## @var editbox
	# the QLineEdit that does the actual editting.

	## constructor.
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		label=QLabel(self)
		label.setText("ValueEditor")
		vbox.addWidget(label)

		self.namelabel=QLabel(self)
		vbox.addWidget(self.namelabel)

		self.typelabel=QLabel(self)
		vbox.addWidget(self.typelabel)

		self.editbox=QLineEdit(self)
		vbox.addWidget(self.editbox)
		vbox.addStretch()
	
		QObject.connect(self.editbox, SIGNAL("editingFinished()"),
			self.editFinished)
		QObject.connect(self.editbox, SIGNAL("returnPressed()"),
			self.editFinished)

	## hook up the ValueEditor with the TreeWidget item.
	def set_treewidget(self, widgetitem):
		self.widgetitem = widgetitem
		fd = widgetitem.field_desc

		T=fd.type
		
		self.typelabel.setText(FD.type_map[T])

		self.namelabel.setText(fd.name)
		if T==FD.STRING:
			self.editbox.setText( widgetitem.get_value())
		else:	
			self.editbox.setText( unicode(widgetitem.get_value()))

		if T in [FD.DOUBLE, FD.FLOAT] :
			self.editbox.setValidator( QDoubleValidator(self.editbox))
		elif T in [FD.UINT32, FD.UINT64]:
			self.editbox.setValidator( QIntValidator(self.editbox0, 0x7fffffff))
		elif T != FD.STRING:
			self.editbox.setValidator( QIntValidator(self.editbox))
		else:
			self.editbox.setValidator(None)
		self.editbox.selectAll()
		self.editbox.setFocus()	

	## slot that is called on pressing enter.
	def editFinished(self) :
		v = unicode(self.editbox.text())
		fd = self.widgetitem.field_desc

		if  fd.type == FD.STRING :
			self.widgetitem.set_value(v)
		elif fd.type in [FD.DOUBLE, FD.FLOAT]:
			self.widgetitem.set_value(float(v))
		else:
			self.widgetitem.set_value(int(v))

		self.widgetitem.treeWidget().emit_gpbupdate()




