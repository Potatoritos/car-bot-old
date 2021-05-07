#include <Python.h>
#include <random>
#include <algorithm>

std::random_device rd;
std::mt19937 e2(rd());
std::uniform_real_distribution<> dist(0, 1);

struct AK_PullSettings {
    float probGE5 = 0.1, probGE6 = 0.02, pity6Inc = 0.02,
          prob5RateUp = 0.5, prob6RateUp = 0.5;
    int pity5 = 10, pity6 = 50, size5Pool = 3, size6Pool = 2,
        since5 = 0, since6 = 0, pity5Amt = 1;
};

struct AK_SimulationResult {
    float expected[6] = {0}, probAmt[6][7] = {0};
};

int8_t AK_pull(float chanceGE5, float chanceGE6, AK_PullSettings &ps) {
    float r1 = dist(e2);
    if (r1 <= chanceGE6) {
        if (dist(e2) <= ps.prob6RateUp) {
            if (dist(e2) <= 1.0f/ps.size6Pool) return 0;
            else return 1;
        } else return 2;
    } else if (r1 <= chanceGE5){
        if (dist(e2) <= ps.prob5RateUp) {
            if (dist(e2) <= 1.0f/ps.size5Pool) return 3;
            else return 4;
        } else return 5;
    }
    return -1;
}

void AK_pullMultiple(int *results, int amt, AK_PullSettings &ps) {
    int since5 = ps.since5, since6 = ps.since6;
    int pity5s = 0;

    for (int i = 0; i < amt; ++i) {
        float chanceGE5;
        if (pity5s < ps.pity5Amt && since5 >= ps.pity5-1) {
            pity5s++;
            chanceGE5 = 1;
        } else {
            chanceGE5 = ps.probGE5;
        }
        float chanceGE6 = std::max(ps.probGE6, (since6-ps.pity6+2) * ps.pity6Inc);

        int8_t p = AK_pull(chanceGE5, chanceGE6, ps);
        if (p == -1) {
            since5++;
            since6++;
            continue;
        }
        results[p]++;
        if (p == 0) results[1]++;
        if (p <= 1) results[2]++;
        if (p == 3) results[4]++;
        if (p == 3 || p == 4) results[5]++;
        since5 = 0;
        pity5s++;
        if (p <= 2) since6 = 0;
    }
}

AK_SimulationResult AK_simulatePulls(int times, int amtPulls, AK_PullSettings ps) {
    AK_SimulationResult sr;
    for (int i = 0; i < times; ++i) {
        int loc_results[6] = {0};
        AK_pullMultiple(loc_results, amtPulls, ps);
        for (int j = 0; j < 6; ++j) {
            sr.probAmt[j][std::min(6, loc_results[j])]++;
            sr.expected[j] += loc_results[j];
        }
    }
    for (int i = 0; i < 6; ++i) {
        sr.expected[i] /= times;
        for (int j = 0; j < 7; ++j) {
            sr.probAmt[i][j] /= times;
        }
    }
    return sr;
}

static PyObject *ak_pull(PyObject *self, PyObject *args, PyObject *kwargs) {
    static const char *kwlist[] = {
        "times", "pull_amount", "prob_ge5", "prob_ge6",
        "pity6_inc", "prob_5rateup", "prob_6rateup", "pity5",
        "pity6", "size_5pool", "size_6pool", "since5",
        "since6", "pity5_amt", NULL
    }; 
    int times, amtPulls;
    float probGE5 = 0.1, probGE6 = 0.02, pity6Inc = 0.02,
           prob5RateUp = 0.5, prob6RateUp = 0.5;
    int pity5 = 10, pity6 = 50, size5Pool = 3, size6Pool = 2,
        since5 = 0, since6 = 0, pity5Amt = 1;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iifffffiiiiiii", const_cast<char**>(kwlist),
                &times, &amtPulls, &probGE5, &probGE6, &pity6Inc, &prob5RateUp,
                &prob6RateUp, &pity5, &pity6, &size5Pool, &size6Pool, &since5, &since6,
                &pity5Amt)) {
        return NULL;
    }
    AK_PullSettings ps = {
        probGE5, probGE6, pity6Inc, prob5RateUp, prob6RateUp,
        pity5, pity6, size5Pool, size6Pool, since5, since6, pity5Amt
    };
    AK_SimulationResult sr = AK_simulatePulls(times, amtPulls, ps);

    PyObject *py_list = PyList_New(6);
    for (int i = 0; i < 6; ++i) { 
        PyObject *py_tuple = Py_BuildValue("ffffffff",
                sr.expected[i], sr.probAmt[i][0], sr.probAmt[i][1],
                sr.probAmt[i][2], sr.probAmt[i][3], sr.probAmt[i][4],
                sr.probAmt[i][5], sr.probAmt[i][6]);
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
