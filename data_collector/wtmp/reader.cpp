#include "reader.h"
#include <utmp.h>

reader::reader()
{
    utmpname(WTMP_FILE);
    fsm = new FSM(0);
}

int reader::next(long &t_sta, long &t_end)
{
  struct utmp *p_utmp;
  int type = -1;
  int tran_type = -1;
  long t, sta;
  do{
      type = tran_type;
      p_utmp = getutent();
      if(p_utmp==NULL){
          break;
      }
      t = p_utmp->ut_tv.tv_sec;
      if(string(p_utmp->ut_user) == "shutdown"){
          tran_type = fsm->trans(0, t, sta);
      }else if(string(p_utmp->ut_user) == "reboot"){
          tran_type = fsm->trans(1, t, sta);
      }
  }while(tran_type!=0);
  if(p_utmp==NULL){
      type = -1; // end of log
      t_sta = 0;
      t_end = 0;
  }else{
      t_sta = sta;
      t_end = t;
  }
  return type;  // 1: normal reboot,  2: crash reboot,  -1: end of log
}

