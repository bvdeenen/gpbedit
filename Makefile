protofiles=$(shell ls *.proto)
generated_python_files=$(protofiles:%.proto=%_pb2.py)

all: $(generated_python_files)



$(generated_python_files) : %_pb2.py : %.proto
	protoc --python_out=. $<
