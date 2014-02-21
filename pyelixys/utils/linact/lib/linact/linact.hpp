#ifndef LINACT_H
#define LINACT_H

#include <linactregdefs.h>
#include <linactbuf.h>
#include <cstdio>
#include <cstring>


#if DBGLINACTBUF
#define LINACTDBG(x, ...) std::printf("[LinAct:DBG]"x"\r\n", ##__VA_ARGS__);
#define LINACTWARN(x, ...) std::printf("[LinAct:WARN]"x"\r\n", ##__VA_ARGS__);
#define LINACTERR(x, ...) std::printf("[LinAct:ERR]"x"\r\n", ##__VA_ARGS__);
#else
#define LINACTDBG(x, ...)
#define LINACTWARN(x, ...)
#define LINACTERR(x, ...)
#endif

#define LINACTINFO(x, ...) std::printf("[LinAct:INFO]"x"\r\n", ##__VA_ARGS__);



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

