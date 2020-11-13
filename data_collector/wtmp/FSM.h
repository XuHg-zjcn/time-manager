#ifndef FSM_H
#define FSM_H

#include <map>
#include <cstring>
using namespace std;

class tran{
    public:
        tran(int i0, int i1);
        friend bool operator<(const tran &k1, const tran &k2);
    private:
        int data[2];
};

typedef class map<tran, int> tab;
typedef class pair<tran, int> pair_t;

class FSM{
    public:
        FSM(int stat0);
        virtual ~FSM();
        int trans(int new_stat, long time, long &sta);

    protected:

    private:
        tab table;
        int stat;
        long last_sta;
};

#endif // FSM_H
