#include <Python.h>
#include <string>
#include <vector>
#include <queue>
#include <algorithm>

int edit_dist(std::string &s, std::string &t, int w_del=1, int w_ins=1, int w_sub=1) {
    int dist[2][t.size() + 1];

    for (unsigned int i = 0; i <= t.size(); ++i)
        dist[0][i] = i * w_ins;

    for (unsigned int i = 1; i <= s.size(); ++i) {
        dist[i % 2][0] = i * w_del;        

        for (unsigned int j = 1; j <= t.size(); ++j) {
            if (s[i-1] == t[j-1]) {
                dist[i % 2][j] = dist[(i-1) % 2][j-1];
            } else {
                dist[i % 2][j] = std::min({
                    w_del + dist[(i-1) % 2][j],
                    w_ins + dist[i % 2][j-1],
                    w_sub + dist[(i-1) % 2][j-1]
                });
            }
        }
    }

    return dist[s.size() % 2][t.size()];
}

static PyObject *func_edit_dist(PyObject *self, PyObject *args) {
    PyObject *obj1, *obj2;
    int w_del, w_ins, w_sub;

    if (!PyArg_ParseTuple(args, "OOiii", &obj1, &obj2, &w_del, &w_ins, &w_sub))
        return NULL;

    if (!PyUnicode_Check(obj1) || !PyUnicode_Check(obj2)) {
        PyErr_SetString(PyExc_TypeError, "must be str");
        return NULL;
    }

    std::string s = PyUnicode_AsUTF8(obj1), t = PyUnicode_AsUTF8(obj2);

    return Py_BuildValue("i", edit_dist(s, t, w_del, w_ins, w_sub));
}

static PyObject *fuzzy_match(PyObject *self, PyObject *args) {
    PyObject *obj, *lobj;
    unsigned int amount;

    if (!PyArg_ParseTuple(args, "OOI", &obj, &lobj, &amount))
        return NULL;

    if (!PyUnicode_Check(obj)) {
        PyErr_SetString(PyExc_TypeError, "must be str");
        return NULL;
    }

    std::string query = PyUnicode_AsUTF8(obj);
    std::vector<std::string> against;

    for (int i = 0; i < PyList_Size(lobj); ++i) {
        if (!PyUnicode_Check(PyList_GetItem(lobj, i))) {
            PyErr_SetString(PyExc_TypeError, "must be a list of str");
            return NULL;
        }
        against.push_back(PyUnicode_AsUTF8(PyList_GetItem(lobj, i)));
    }

    std::priority_queue<std::pair<int, int>> best;

    for (unsigned int i = 0; i < against.size(); ++i) {
        int dist = edit_dist(query, against[i], 10, 1, 10);
        best.push({dist, i});
        if (best.size() > amount) best.pop();
    }
    
    std::vector<std::pair<int, int>> ret;

    while (!best.empty()) {
        ret.push_back(best.top());
        best.pop();
    }

    PyObject *py_list = PyList_New(amount);

    for (unsigned int i = 0; i < amount; ++i) {
        PyObject *py_tuple = Py_BuildValue("ii", ret[amount-i-1].second, ret[amount-i-1].first);
        PyList_SetItem(py_list, i, py_tuple);
    }

    return py_list;
}

static PyMethodDef methods[] = {
    {"fuzzy_match", fuzzy_match, METH_VARARGS, "Returns the indices and edit distances of the most similar strings"},
    {"edit_dist", func_edit_dist, METH_VARARGS, "Returns the edit distance of two strings"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef string_stuff = {
    PyModuleDef_HEAD_INIT,
    "string_stuff",
    "Utility functions for strings",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_string_stuff(void) {
    return PyModule_Create(&string_stuff);
}
