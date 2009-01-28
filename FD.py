#!/usr/bin/python
# vim:tw=120

from google.protobuf.descriptor import FieldDescriptor

global type_map, label_map

# return a dictionary with value:name pairs for constants in a field object
# like 
#  1  : 'DOUBLE',
#  2  : 'FLOAT',
#  3  : 'INT64',
#  4  : 'UINT64',
#  5  : 'INT32',
#  6  : 'FIXED64',
#  7  : 'FIXED32',
#  8  : 'BOOL',
#  9  : 'STRING',
#  10 : 'GROUP',
#  11 : 'MESSAGE',
#  12 : 'BYTES',
#  13 : 'UINT32',
#  14 : 'ENUM',
#  15 : 'SFIXED32',
#  16 : 'SFIXED64',
#  17 : 'SINT32',
#  18 : 'SINT64'
#  
#  1  : 'OPTIONAL',
#  2  : 'REQUIRED',
#  3  : 'REPEATED'

def create_value_map(object,prefix):
	M={}
	types = [(getattr(object,m),m[len(prefix):]) for m in dir(object) \
		if not callable(getattr(object,m)) and m.startswith(prefix)]
	for key,value in types:
		M[key]=value
		globals()[value]=key	
	return M	

def init():
	global type_map, label_map
	type_map=create_value_map(FieldDescriptor,"TYPE_")
	label_map=create_value_map(FieldDescriptor,"LABEL_")



if __name__ == '__main__':
	init()
	print type_map
	print label_map
	

