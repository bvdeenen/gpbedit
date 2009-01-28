#!/usr/bin/python
# vim:tw=120

from google.protobuf.descriptor import FieldDescriptor

global type_map, label_map

# return a dictionary with value:name pairs for constants in a field object
# like 
#  1  : 'TYPE_DOUBLE',
#  2  : 'TYPE_FLOAT',
#  3  : 'TYPE_INT64',
#  4  : 'TYPE_UINT64',
#  5  : 'TYPE_INT32',
#  6  : 'TYPE_FIXED64',
#  7  : 'TYPE_FIXED32',
#  8  : 'TYPE_BOOL',
#  9  : 'TYPE_STRING',
#  10 : 'TYPE_GROUP',
#  11 : 'TYPE_MESSAGE',
#  12 : 'TYPE_BYTES',
#  13 : 'TYPE_UINT32',
#  14 : 'TYPE_ENUM',
#  15 : 'TYPE_SFIXED32',
#  16 : 'TYPE_SFIXED64',
#  17 : 'TYPE_SINT32',
#  18 : 'TYPE_SINT64'
#  
#  1  : 'LABEL_OPTIONAL',
#  2  : 'LABEL_REQUIRED',
#  3  : 'LABEL_REPEATED'

def create_value_map(object,prefix):
	M={}
	types = [(getattr(object,m),m) for m in dir(object) \
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
	

