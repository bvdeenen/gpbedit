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
		descriptor=container.DESCRIPTOR
		self.fd = fd
		self.container= container

		t=FD.type_map[self.fd.type]
		self.typelabel.setText(t)

		self.namelabel.setText(fd.name)
		if self.fd.type==FD.STRING:
			self.editbox.setText( getattr(container, fd.name).decode('utf-8'))
		else:	
			self.editbox.setText( str(getattr(container, fd.name)))
		self.editbox.setFocus()	

	def editFinished(self) :
		v = unicode(self.editbox.text())

		if  self.fd.type == FD.STRING :
			setattr(self.container, self.fd.name, v.encode('utf-8'))

		elif self.fd.type in [FD.DOUBLE, FD.FLOAT]:
			setattr(self.container, self.fd.name, float(v))
		else:
			setattr(self.container, self.fd.name, int(v))

		self.widgetitem.set_column_data()
		self.widgetitem.treeWidget().emit_gpbupdate()




