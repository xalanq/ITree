#!/usr/bin/python3

import itreefile, sys

name = sys.argv[1]

op = itreefile.ITreeFile(name)

x = itreefile.INode()
y = itreefile.IResNode()

op.open(x, y)

def debug1(x, tab=''):
	for i in range(x.len()):
		y = x.at(i)
		print('{}[{}, {}]'.format(tab, y.name, y.text))
		debug1(y, tab+'  ')

def debug2(x, tab=''):
	c = x.childrenInfo()
	for info in c:
		print('{}{} - {}'.format(tab, info.name, info.isFile))
		debug2(x.at(x.findName(info.name)), tab+'  ')

debug1(x)
print('')
debug2(y)

op.write(x, y)

