#!/usr/bin/python

from example_pb2 import *
from effects_pb2 import *
from rows_pb2 import *

global type_map, label_map
type_map={}
label_map={}

def create_label_map(object):
	global label_map
	types = [(getattr(object,m),m) for m in dir(object) \
		if not callable(getattr(object,m)) and m.startswith("LABEL_")]
	for key,value in types:
		label_map[key]=value
def create_typemap(object):
	global type_map
	types = [(getattr(object,m),m) for m in dir(object) \
		if not callable(getattr(object,m)) and m.startswith("TYPE_")]
	for key,value in types:
		type_map[key]=value
	
def show_message(descriptor, l=0):
	global type_map, label_map
	if not descriptor: return
	#print " "*l, descriptor.name
	fields = descriptor.fields_by_name
	for k,v in fields.items():
		if not type_map: create_typemap(v)
		if not label_map: create_label_map(v)

		typename = ""
		if v.message_type: typename = v.message_type.name
		elif v.enum_type: typename = v.enum_type.name
		default_value=""
		if v.default_value : default_value="default:%s" % (v.default_value,)
		print "   ", " "*l, k, type_map[v.type], typename, \
			label_map[v.label], default_value, "{"
		
		# recurse
		show_message(v.message_type, l+4)
		show_enum(v.enum_type, l+4)
		print "   ", " "*l, "}"
			


def show_enum(descriptor,l=0):
	if not descriptor: return
	#print " "*l, descriptor.name
	fields = descriptor.values_by_name
	for k in fields.keys():
		print "  ", " "*l, k
	
def test( object ) :
	print object.name
	show_message(object)


if __name__ == '__main__' :
	test(ILNMessage.DESCRIPTOR)

