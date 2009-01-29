protofiles=$(shell ls *.proto)
generated_python_files=$(protofiles:%.proto=%_pb2.py)

sourcefiles=booleaneditor.py debugwidget.py enumeditor.py FD.py gpbedit.py itemeditor.py messageeditor.py settings.py valueeditor.py
all: $(generated_python_files) doc

doc: $(sourcefiles)
	epydoc $(sourcefiles)

$(generated_python_files) : %_pb2.py : %.proto
	protoc --python_out=. $<

clean:
	-rm $(generated_python_files)
	-rm *.pyc
