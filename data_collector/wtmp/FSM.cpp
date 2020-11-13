#include "FSM.h"
#include <iostream>

using namespace std;

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
    //pair_t(tran(old_stat, new_stat), return)
    this->stat = stat0;
    this->last_sta = 0;
    this->table.insert(pair_t(tran(0, 1), 1));  // reboot
    this->table.insert(pair_t(tran(1, 0), 0));  // shutdown
    this->table.insert(pair_t(tran(1, 1), 2));  // crash and boot
}

FSM::~FSM()
{
    //dtor
}

int FSM::trans(int new_stat, long time, long &sta)
{
    tran key = tran(stat, new_stat);
    stat = new_stat;
    int ret = table[key];
    if(ret!=0){  // reboot or, crash and reboot
       last_sta = time;  //save start time
    }else{       // shutdown
       sta = last_sta;   //output last start time
    }
    return ret;
}
