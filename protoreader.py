#!/usr/bin/python

from example_pb2 import *
from effects_pb2 import *
from rows_pb2 import *

def test( filename ) :
	print "contents of ILNMessage"
	descriptor= ILNMessage.DESCRIPTOR
	fields = descriptor.fields_by_name
	for k in fields.keys():
		print "="*20, k, "*"*20
		f2=fields[k].message_type.fields_by_name
		for k2 in f2.keys():
			print "   ", k2


if __name__ == '__main__' :
	test('example.proto')

