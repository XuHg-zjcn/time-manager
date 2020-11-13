#include "FSM.h"
#include <map>
using namespace std;


tran::tran(int i2[2]){
    memcpy(data, i2, sizeof(int)*2);
}
tran::tran(int i0, int i1){
    data[0] = i0;
    data[1] = i1;
}

bool operator<(const tran &k1, const tran &k2){
    if(k1.data[0] < k2.data[0]){
        return true;
    }else if(k1.data[0] == k2.data[1]){
        return k1.data[1] < k2.data[1];
    }else{
        return false;
    }
}

FSM::FSM(int stat0)
{
    this->stat = stat0;
    this->table.insert(pair_t(tran(0, 1), 1));  // boot
    this->table.insert(pair_t(tran(1, 0), 0));  // shutdown
    this->table.insert(pair_t(tran(1, 1), 1));  // crash and boot
}

FSM::FSM(int stat0, tab table)
{
    //ctor
    this->table = table;
    this->stat = stat0;
}

FSM::~FSM()
{
    //dtor
}

int FSM::trans(int act)
{
    int i2[2] = {stat, act};
    tran key = tran(i2);
    stat = table[key];
    return stat;
}
