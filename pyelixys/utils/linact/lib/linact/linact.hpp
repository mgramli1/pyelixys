#ifndef LINACT_H
#define LINACT_H

#include <linactregdefs.h>
#include <linactbuf.h>
#include <cstdio>
#include <cstring>



namespace IAI {

  class LinearActuator {

    public:
        LinActBuf buffer;
        LinActBuf inbuf;
        LinearActuator();
        ~LinearActuator();
        unsigned short getAxisReadAddress(unsigned int axisid);
        unsigned short getAxisWriteAddress(unsigned int axisid);
        LinActBuf * getGwStatusStr();
        LinActBuf * getGwStartStr();
        LinActBuf * getAxisStatus(unsigned int axisid);
        LinActBuf * getAxisPos(unsigned int axisid);
        LinActBuf * getSetAxisPos(unsigned int axisid,
                unsigned int position);
        LinActBuf * getAxisStart(unsigned int axisid);
        LinActBuf * getAxisPause(unsigned int axisid);
        LinActBuf * getAxisReset(unsigned int axisid);
        LinActBuf * getAxisHome(unsigned int axisid);
        LinActBuf * getAxisBrakeRelease(unsigned int axisid);

        void send();
        LinActBuf * receive(int len);
  };

}

#endif /* LINACT_H */

