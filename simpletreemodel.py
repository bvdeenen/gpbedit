#!/usr/bin/env python

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

    

class TreeItem:
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        return self.itemData[column]

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)

        rootData = []
        rootData.append(QtCore.QVariant("Name"))
        rootData.append(QtCore.QVariant("Type"))
        rootData.append(QtCore.QVariant("Kind"))
        rootData.append(QtCore.QVariant("Default"))
        self.rootItem = TreeItem(rootData)
        self.analyze_message(data, self.rootItem)
        

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        item = index.internalPointer()

        return QtCore.QVariant(item.data(index.column()))

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return QtCore.QVariant()

    def index(self, row, column, parent):
        if row < 0 or column < 0 or row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()


    # show the structure of a message descriptor
    def analyze_message(self,descriptor, parent, l=0):
        global type_map, label_map
        if not descriptor: return
        #print " "*l, descriptor.name
        fields = descriptor.fields_by_number
        for key,value in fields.items():

            if not type_map: type_map=create_value_map(value,"TYPE_")
            if not label_map: label_map=create_value_map(value,"LABEL_")

            if value.message_type: typename = value.message_type.name
            elif value.enum_type: typename = value.enum_type.name
            else: typename = ""

            if value.default_value : default_value="default:%s" % (value.default_value,)
            else: default_value=""

            d = []
            d.append(QtCore.QVariant(value.name))
            d.append(QtCore.QVariant(type_map[value.type]))
            d.append(QtCore.QVariant(typename))
            d.append(QtCore.QVariant(label_map[value.label]))
            d.append(QtCore.QVariant(default_value))

            child = TreeItem(d,parent)
            parent.appendChild(child)
            # recurse
            self.analyze_message(value.message_type, child, l+4)
            self.show_enum(value.enum_type, child, l+4)
                


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


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    #f = QtCore.QFile("default.txt")
    #f.open(QtCore.QIODevice.ReadOnly)
    model = TreeModel(PB_OBJECT.DESCRIPTOR)
    #f.close()

    view = QtGui.QTreeView()
    view.setModel(model)
    view.setWindowTitle("Simple Tree Model")
    view.show()
    sys.exit(app.exec_())
