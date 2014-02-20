#ifndef LINACT_H
#define LINACT_H

#include <linactregdefs.h>
#include <linactbuf.h>
#include <cstdio>
#include <cstring>



namespace IAI {

  const float NOTPOSMSGERR = -999999.0;

  class LinearActuator {

    public:
        LinActBuf buffer;
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

        float getPosition();

        LinActBuf * getBuffer();

        void send();
        LinActBuf * receiveStdin(int len);

        LinActBuf * pushByteRxBuffer(char c);

        int checkChecksum();

  };

}

#endif /* LINACT_H */

