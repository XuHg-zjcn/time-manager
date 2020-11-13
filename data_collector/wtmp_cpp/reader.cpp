#include <iostream>
#include <iomanip>
#include <utmp.h>
#include <ctime>
#include <FSM.h>

using namespace std;

int main(int argc, char *argv[])
{
  struct utmp *p_utmp;
  utmpname(WTMP_FILE);
  long t;
  struct tm *p_tm;
  char *str_time = (char*)malloc(32);
  const char *time_fmt= "%Y-%m-%d %H:%M:%S";
  int status;
  while(1){
      p_utmp = getutent();
      if(p_utmp==NULL){
        break;
      }
      t = p_utmp->ut_tv.tv_sec;
      p_tm = localtime(&t);
      strftime(str_time, 32, time_fmt, p_tm);
      cout << str_time << ' '
           << dec << p_utmp->ut_type << ' '
           << setfill(' ')<<setw(20) << p_utmp->ut_host << ' '
           << setfill(' ')<<setw(10) << p_utmp->ut_user << ' '
           << setfill(' ')<<setw(10) << p_utmp->ut_line << ' ' << endl;
      /*
      7: shutdown
      */
  }
}
