#include <iostream>
#include <iomanip>
#include <ctime>
#include <reader.h>
#include <utmp.h>
int main(int argc, char *argv[]){
    reader r = reader();
    int type = 0;
    int n = 0;
    long t_sta;
    long t_end;
    char *str_time = new char[32];
    const char *time_fmt = "%Y-%m-%d %H:%M:%S";
    while(true){
        type = r.next(t_sta, t_end);
        if(type == -1)
            break;
        cout << setw(2) << type << "  ";
        strftime(str_time, 32, time_fmt, localtime(&t_sta));
        cout << str_time << " ||| ";
        strftime(str_time, 32, time_fmt, localtime(&t_end));
        cout << str_time << endl;
        n++;
    }
    cout << "found " << n << endl;
    return 0;
}
