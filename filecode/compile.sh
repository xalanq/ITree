#!/usr/bin/bash

name=$1
swig -python -c++ ${name}.i
g++ -fPIC -Wall -Wextra -shared ${name}.cpp ${name}_wrap.cxx -o _${name}.so -I/usr/include/python3.4m/

rm ${name}_wrap.cxx
# g++ -fPIC -Wall -Wextra -shared ${name}.cpp -o lib${name}.so
