class Generic_class
integer = ...
file = ..

...

def func(rdd)
	...
	rdd.map(lambda X : X + integer).filter(...)
	...
..

WHY IS THIS A BAD CLASS:

local Variable and spark:
1) Each Node gets a copy of a Varible (no sync)
2) Variables must be serializable
	serializables: 
		all base types (int, etc)
		containers with serializables
		custom classes and types that are made serializabels
	not serializables:
		files
		
3) Use field of object -> whole object gets transfered to the nodes

