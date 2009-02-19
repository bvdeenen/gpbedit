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
		container = widgetitem.parent().gpbitem

		self.typelabel.setText(FD.type_map[fd.type])

		self.namelabel.setText(fd.name)
		if fd.type==FD.STRING:
			self.editbox.setText( getattr(container, fd.name))
		else:	
			self.editbox.setText( str(getattr(container, fd.name)))

		print "fd.type=",fd.type
		if fd.type in [FD.DOUBLE, FD.FLOAT] :
			self.editbox.setValidator( QDoubleValidator(self.editbox))
		elif fd.type in [FD.UINT32, FD.UINT64]:
			self.editbox.setValidator( QIntValidator(self.editbox0, 0x7fffffff))
		elif fd.type != FD.STRING:
			self.editbox.setValidator( QIntValidator(self.editbox))
		self.editbox.selectAll()
		self.editbox.setFocus()	

	def editFinished(self) :
		v = unicode(self.editbox.text())
		fd = self.widgetitem.field_desc
		container = self.widgetitem.parent().gpbitem

		if  fd.type == FD.STRING :
			setattr(container, fd.name, v)
		elif fd.type in [FD.DOUBLE, FD.FLOAT]:
			setattr(container, fd.name, float(v))
		else:
			setattr(container, fd.name, int(v))

		self.widgetitem.set_column_data()
		self.widgetitem.treeWidget().emit_gpbupdate()




