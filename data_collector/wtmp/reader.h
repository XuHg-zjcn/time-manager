#include <utmp.h>
#include "FSM.h"

class reader{
    public:
        reader(void);
        int next(long &t_sta, long &t_end);
    private:
        FSM *fsm;
};
