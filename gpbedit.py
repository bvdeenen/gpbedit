#!/usr/bin/env python
# vim:tw=120

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from example_pb2 import *
from effects_pb2 import *
from rows_pb2 import *

global type_map, label_map
type_map={}
label_map={}

# return a dictionary with value:name pairs for constants in a field object
# like 
# {1: 'TYPE_DOUBLE', 2: 'TYPE_FLOAT', 3: ...
def create_value_map(object,prefix):
	M={}
	types = [(getattr(object,m),m) for m in dir(object) \
		if not callable(getattr(object,m)) and m.startswith(prefix)]
	for key,value in types:
		M[key]=value
	return M	

class EnumEditor(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
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
		itemdata=widgetitem.itemData
		self.namelabel.setText(itemdata.name)
		self.enumtypelabel.setText(itemdata.enum_type.name)

		self.enumpopup.clear()

		for key,value in itemdata.enum_type.values_by_number.items():
			action = self.enumpopup.addAction("%d %s" %( value.number, value.name))
			if  key == itemdata.default_value :
				self.enumpopup.setActiveAction( action)


class ItemEditor(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		self.stack = QStackedWidget(self)

		vbox.addWidget(self.stack)
		vbox.addStretch()

		self.okbutton=QPushButton(self)
		self.okbutton.setText("save")

		vbox.addWidget(self.okbutton)
		QObject.connect(self.okbutton,
			SIGNAL('clicked()'),
			self.okbuttonclicked)

		self.enumeditor=EnumEditor(self.stack)
		self.stack.addWidget(self.enumeditor)


	def okbuttonclicked(self):
		print "klik"

	def make_connections(self, treewidget):
		QObject.connect(treewidget, 
			SIGNAL('itemClicked ( QTreeWidgetItem *, int )'),
			self.slot_treeitem_click)

	
	def slot_treeitem_click(self, widgetitem, column):
		itemdata=widgetitem.itemData
		#print itemdata, column
		if itemdata.enum_type:
			self.enumeditor.set_treewidget(widgetitem)
	

class TreeItem(QTreeWidgetItem):
	def __init__(self, descriptor, parent=None, labels=[]):
		QTreeWidgetItem.__init__(self,parent)
		self.itemData = descriptor
	# analyze the structure of a gpb message descriptor and create TreeItems
	# based on that structure
	#def analyze_message(self,descriptor, parent, l=0):
		if not labels:
			self.setText(0,descriptor.name)
		else:
			for i,l in enumerate(labels): self.setText(i,str(l))

		if not descriptor: return
		if not hasattr(descriptor,'fields_by_number'): return

		global type_map, label_map

		fields = descriptor.fields_by_number
		for key,value in fields.items():

			if not type_map: type_map=create_value_map(value,"TYPE_")
			if not label_map: label_map=create_value_map(value,"LABEL_")

			if value.message_type: typename = value.message_type.name
			elif value.enum_type: typename = value.enum_type.name
			else: typename = type_map[value.type]

			if value.default_value : 
				if value.enum_type:
					default_value = value.enum_type.values_by_number[value.default_value].name
				else:	
					default_value=str(value.default_value)
			else: 
				default_value=""

			labels=[value.name, value.type,typename,label_map[value.label], default_value]
			# recurse
			if ( value.message_type ) :
				TreeItem(value.message_type, self,labels)
			else:	
				TreeItem(value,self, labels)
			#child.show_enum(value.enum_type, child, l+4)



class TreeWidget(QTreeWidget):
	def __init__(self, parent=None):
		QTreeWidget.__init__(self, parent)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	mainwindow=QWidget()
	layout = QHBoxLayout(mainwindow)
	mainwindow.setLayout(layout)

	widget = TreeWidget()
	widget.setWindowTitle("Simple Tree Model")
	widget.setHeaderLabels( [ "Name" ,"Type" ,"Kind" ,"Label" ,"Default"])
	widget.addTopLevelItem(TreeItem(PB_OBJECT.DESCRIPTOR))

	layout.addWidget(widget)

	editwidget = ItemEditor(mainwindow)
	layout.addWidget(editwidget)

	editwidget.make_connections(widget)

	mainwindow.show()
	sys.exit(app.exec_())
