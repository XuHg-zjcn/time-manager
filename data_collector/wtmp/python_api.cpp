#include <Python.h>
#include <reader.h>
extern "C"{
    PyObject* __iter__(PyObject* self);
    PyObject* __next__(PyObject* self);
    PyMODINIT_FUNC PyInit_libwtmp_cpp(void);
}

reader r;

PyObject* next(PyObject* self, PyObject* args)
{
    long t_sta=0, t_end=0;
    int type = r.next(t_sta, t_end);
    return Py_BuildValue("lli", t_sta, t_end, type);
}

static PyMethodDef module_methods[] =
{
  {"next", next, METH_NOARGS, "next_dt"},
  {NULL}
};

static PyModuleDef wtmp_cpp =
{
  PyModuleDef_HEAD_INIT,
  "wtmp_cpp",
  "read wtmp to python",
  -1,
  module_methods
};

PyMODINIT_FUNC PyInit_libwtmp_cpp(void)
{
  return PyModule_Create(&wtmp_cpp);
}
