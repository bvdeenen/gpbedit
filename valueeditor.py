# vim:tw=120
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import FD

class ValueEditor(QWidget):
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

		print fd.type
		if T in [FD.DOUBLE, FD.FLOAT] :
			print "QDoubleValidator"
			self.editbox.setValidator( QDoubleValidator(self.editbox))
		elif T in [FD.UINT32, FD.UINT64]:
			self.editbox.setValidator( QIntValidator(self.editbox0, 0x7fffffff))
			print "QIntValidator"
		elif T != FD.STRING:
			self.editbox.setValidator( QIntValidator(self.editbox))
			print "QIntValidator"
		else:
			self.editbox.setValidator(None)
		self.editbox.selectAll()
		self.editbox.setFocus()	

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




