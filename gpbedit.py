#!/usr/bin/env python
# vim:tw=120

import sys
from PyQt4 import QtCore, QtGui

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

	

class TreeItem(QtGui.QTreeWidgetItem):
	def __init__(self, descriptor, parent=None, labels=[]):
		QtGui.QTreeWidgetItem.__init__(self,parent)
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

	def show_enum(self, descriptor, parent ,l=0):
		if not descriptor: return
		#print " "*l, descriptor.name
		fields = descriptor.values_by_number
		for k,value in fields.items():
			#print " ", " "*l, v.name, v.number
			d = []
			d.append(QtCore.QVariant(value.name))
			d.append(QtCore.QVariant(value.number))
			d.append(QtCore.QVariant(""))
			d.append(QtCore.QVariant(""))
			d.append(QtCore.QVariant(""))
			child = parent.appendChild(TreeItem(d,parent))


class TreeWidget(QtGui.QTreeWidget):
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)

	widget = TreeWidget()
	widget.setWindowTitle("Simple Tree Model")
	widget.setHeaderLabels( [ "Name" ,"Type" ,"Kind" ,"Label" ,"Default"])
	widget.addTopLevelItem(TreeItem(PB_OBJECT.DESCRIPTOR))
	widget.show()
	sys.exit(app.exec_())
