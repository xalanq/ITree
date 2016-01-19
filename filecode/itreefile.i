%module itreefile

%include "std_string.i"
%include "std_vector.i"
%include "std_set.i"

%typemap(out) bytes {
    $result = PyBytes_FromStringAndSize($1.c_str(), $1.size());
}

%typemap(in) (const char *, int) {
    if(!PyBytes_Check($input)) {
        PyErr_SetString(PyExc_ValueError,"Expected a bytes string");
        return NULL;
    }
    $1 = PyBytes_AsString($input);
    $2 = PyBytes_Size($input);
}

%{
#include "itreefile.h"
%}

namespace std {
%template(StringVector) vector<string>;
%template(vector_IResNodeInfo) vector<IResNodeInfo>;
}

%include "itreefile.h"
