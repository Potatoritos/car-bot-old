#include <Python.h>
#include <algorithm>
#include <random>

std::random_device rd;
std::mt19937 e2(rd());
std::uniform_real_distribution<> dist(0, 1);

struct AK_PullResult {
    int amt5 = 0, amt6 = 0;
    AK_PullResult& operator+=(AK_PullResult const& other) {
        amt5 += other.amt5;
        amt6 += other.amt6;
        return *this;
    }
};

struct AK_PullSettings {
    double probGE5 = 0.1,
           probGE6 = 0.02,
           pity6Inc = 0.02,
           prob5RateUp = 0.5,
           prob6RateUp = 0.5;
    int pity5 = 10,
        pity6 = 50,
        size5Pool = 3,
        size6Pool = 2,
        since5 = 0,
        since6 = 0;
};

struct AK_SimulationResult {
    int amt5_total = 0, amt6_total = 0;
    double amt5[7]={0}, amt5RateUp[7]={0}, amt5Specific[7]={0},
           amt6[7]={0}, amt6RateUp[7]={0}, amt6Specific[7]={0};
};

AK_PullResult AK_pull(double chanceGE5, double chanceGE6) {
    double r = dist(e2);
    if (r <= chanceGE6)
        return {0, 1};
    else if (r <= chanceGE5)
        return {1, 0};
    return {0, 0};
}

AK_PullResult AK_pullMultiple(int amt, AK_PullSettings &ps) {
    AK_PullResult results, p;
    int since5 = ps.since5, since6 = ps.since6;

    for (int i = 0; i < amt; ++i) {
        double chanceGE6 = std::max(0.02, (since6 - ps.pity6+2) * ps.pity6Inc);
        double chanceGE5 = since5 >= ps.pity5-1 ? 1 : ps.probGE5;

        p = AK_pull(chanceGE5, chanceGE6);
        since6++;
        since5++;
        results += p;
        if (p.amt6) {
            since6 = 0;
            since5 = 0;
        } else if (p.amt5) {
            since5 = 0;
        }
    }
    return results;
}

AK_SimulationResult AK_simulatePulls(int times, int amtPulls, AK_PullSettings ps) {
    AK_PullResult results;
    AK_SimulationResult sr;

    for (int i = 0; i < times; ++i) {
        AK_PullResult p = AK_pullMultiple(amtPulls, ps);
        results += p;

        double a = p.amt5*ps.prob5RateUp;

        double f = std::floor(a), c = std::ceil(a);
        
        if (f != c) { 
            sr.amt5RateUp[std::min(6, (int)f)] += 1 - ps.prob5RateUp;
            sr.amt5RateUp[std::min(6, (int)c)] += ps.prob5RateUp;
        } else {
            sr.amt5RateUp[std::min(6, (int)f)]++;
        }

        a /= ps.size5Pool;
        f = std::floor(a);
        c = std::ceil(a);

        if (f != c) {
            sr.amt5Specific[std::min(6, (int)f)] += 1 - ps.prob5RateUp/ps.size5Pool;
            sr.amt5Specific[std::min(6, (int)c)] += ps.prob5RateUp/ps.size5Pool;
        } else {
            sr.amt5Specific[std::min(6, (int)f)]++;
        }

        sr.amt6[std::min(6, p.amt6)]++;

        a = p.amt6*ps.prob6RateUp;
        f = std::floor(a);
        c = std::ceil(a);
        
        if (f != c) { 
            sr.amt6RateUp[std::min(6, (int)f)] += 1 - ps.prob6RateUp;
            sr.amt6RateUp[std::min(6, (int)c)] += ps.prob6RateUp;
        } else {
            sr.amt6RateUp[std::min(6, (int)f)]++;
        }

        a /= ps.size6Pool;
        f = std::floor(a);
        c = std::ceil(a);

        if (f != c) {
            sr.amt6Specific[std::min(6, (int)f)] += 1 - ps.prob6RateUp/ps.size6Pool;
            sr.amt6Specific[std::min(6, (int)c)] += ps.prob6RateUp/ps.size6Pool;
        } else {
            sr.amt6Specific[std::min(6, (int)f)]++;
        }
    }
    sr.amt5_total = results.amt5;
    sr.amt6_total = results.amt6;
    return sr;
}

static PyObject *ak_pull(PyObject *self, PyObject *args, PyObject *kwargs) {
    static const char *kwlist[] = {
        "times",
        "pull_amount",
        "prob_ge5",
        "prob_ge6",
        "pity6_inc",
        "prob_5rateup",
        "prob_6rateup",
        "pity5",
        "pity6",
        "size_5pool",
        "size_6pool",
        "since5",
        "since6",
        NULL
    };
    int times, amtPulls;
    double probGE5 = 0.1,
           probGE6 = 0.02,
           pity6Inc = 0.02,
           prob5RateUp = 0.5,
           prob6RateUp = 0.5;
    int pity5 = 10,
        pity6 = 50,
        size5Pool = 3,
        size6Pool = 2,
        since5 = 0,
        since6 = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iidddddiiiiii", const_cast<char**>(kwlist),
                &times, &amtPulls, &probGE5, &probGE6, &pity6Inc, &prob5RateUp,
                &prob6RateUp, &pity5, &pity6, &size5Pool, &size6Pool, &since5, &since6)) {
        return NULL;
    }

    AK_PullSettings ps = {
        probGE5, probGE6, pity6Inc, prob5RateUp, prob6RateUp,
        pity5, pity6, size5Pool, size6Pool, since5, since6
    };
    AK_SimulationResult sr = AK_simulatePulls(times, amtPulls, ps);

    double r[6][8] = {0};

    r[0][0] = (double)sr.amt5_total / times;
    r[1][0] = (double)sr.amt5_total * prob5RateUp / times;
    r[2][0] = (double)sr.amt5_total * prob5RateUp / (times*size5Pool);
    r[3][0] = (double)sr.amt6_total / times;
    r[4][0] = (double)sr.amt6_total * prob6RateUp / times;
    r[5][0] = (double)sr.amt6_total * prob6RateUp / (times*size6Pool);
    for (int i = 1; i <= 7; ++i) {
        r[0][i] = (double)sr.amt5[i-1] / times;
        r[1][i] = (double)sr.amt5RateUp[i-1] / times;
        r[2][i] = (double)sr.amt5Specific[i-1] / times;
        r[3][i] = (double)sr.amt6[i-1] / times;
        r[4][i] = (double)sr.amt6RateUp[i-1] / times;
        r[5][i] = (double)sr.amt6Specific[i-1] / times;
    }

    PyObject *py_list = PyList_New(6);
    for (int i = 0; i < 6; ++i) {
        PyObject *py_tuple = Py_BuildValue("dddddddd",
                r[i][0], r[i][1], r[i][2], r[i][3],
                r[i][4], r[i][5], r[i][6], r[i][7]);
        PyList_SetItem(py_list, i, py_tuple);
    }

    return py_list;
}

static PyMethodDef methods[] = {
    {"ak_pull", (PyCFunction)ak_pull, METH_VARARGS | METH_KEYWORDS, "Simulates Arknights pulls"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef simulations = {
    PyModuleDef_HEAD_INIT,
    "simulations",
    "Simulations",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_simulations(void) {
    return PyModule_Create(&simulations);
}
