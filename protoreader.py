#!/usr/bin/python

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

	
# show the structure of a message descriptor
def show_message(descriptor, l=0):
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

		if not value.message_type and not value.enum_type :
			print "   ", " "*l, value.name, type_map[value.type], typename, \
				label_map[value.label], default_value
		else:		
			print "   ", " "*l, value.name, type_map[value.type], typename, \
				label_map[value.label], default_value, "{"
			# recurse
			show_message(value.message_type, l+4)
			show_enum(value.enum_type, l+4)
			print "   ", " "*l, "} //", value.name
			


def show_enum(descriptor,l=0):
	if not descriptor: return
	#print " "*l, descriptor.name
	fields = descriptor.values_by_number
	for k,v in fields.items():
		print " ", " "*l, v.name, v.number
	
def test( object ) :
	print object.name
	show_message(object)


if __name__ == '__main__' :
	test(ILNMessage.DESCRIPTOR)

