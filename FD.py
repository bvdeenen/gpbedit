#!/usr/bin/python
# vim:tw=120

from google.protobuf.descriptor import FieldDescriptor

global type_map, label_map

## @package FD
# build dictionaries with value:name pairs for constants in a field object.

## @var typemap
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
## @var  labelmap
#  1  : 'OPTIONAL',
#  2  : 'REQUIRED',
#  3  : 'REPEATED'



## create the mappings.
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


## @page FD_interactive FD interactive session using idle, the python ide.
#<pre>
#>>> import FD
#>>> FD.init()
#>>> dir(FD)
#['BOOL', 'BYTES', 'DOUBLE', 'ENUM', 'FIXED32', 'FIXED64', 'FLOAT', 'FieldDescriptor', 'GROUP', 'INT32', 'INT64',
#'MESSAGE', 'OPTIONAL', 'REPEATED', 'REQUIRED', 'SFIXED32', 'SFIXED64', 'SINT32', 'SINT64', 'STRING', 'UINT32', 'UINT64',
#'__builtins__', '__doc__', '__file__', '__name__', '__package__', 'create_value_map', 'init', 'label_map', 'type_map']
#>>> fd.BOOL
#
#Traceback (most recent call last):
#  File "<pyshell#3>", line 1, in <module>
#    fd.BOOL
#NameError: name 'fd' is not defined
#>>> FD.BOOL
#8
#>>> FD.type_map
#{1: 'DOUBLE', 2: 'FLOAT', 3: 'INT64', 4: 'UINT64', 5: 'INT32', 6: 'FIXED64', 7: 'FIXED32', 8: 'BOOL', 9: 'STRING', 10:
#'GROUP', 11: 'MESSAGE', 12: 'BYTES', 13: 'UINT32', 14: 'ENUM', 15: 'SFIXED32', 16: 'SFIXED64', 17: 'SINT32', 18:
#'SINT64'}
#>>> FD.REPEATED
#3
#
#</pre>


if __name__ == '__main__':
	init()
	print "type_map", type_map
	print "label_map", label_map
	

