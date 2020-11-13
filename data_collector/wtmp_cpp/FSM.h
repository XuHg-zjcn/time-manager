#ifndef FSM_H
#define FSM_H

#include <map>
#include <cstring>
using namespace std;

class tran{
    public:
        tran(int i2[2]);
        tran(int i0, int i1);
        friend bool operator<(const tran &k1, const tran &k2);
    private:
        int data[2];
};

typedef class map<tran, int> tab;
typedef class pair<tran, int> pair_t;

class FSM
{
    public:
        FSM(int stat0);
        FSM(int stat0, tab table);
        int trans(int act);
        virtual ~FSM();

    protected:

    private:
        tab table;
        int stat;
};

#endif // FSM_H
