#!/usr/bin/python


def test( filename ) :
	proto = open(filename).read()
	print(proto)

if __name__ == '__main__' :
	test('example.proto')

