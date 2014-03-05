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
        LinActBuf * getGwStatusQuery();
        LinActBuf * getGwStartQuery();
        LinActBuf * getAxisStatusQuery(unsigned int axisid);
        LinActBuf * getAxisPosQuery(unsigned int axisid);
        LinActBuf * getSetAxisPosQuery(unsigned int axisid,
                unsigned int position);
        LinActBuf * getAxisStartQuery(unsigned int axisid);
        LinActBuf * getAxisPauseQuery(unsigned int axisid);
        LinActBuf * getAxisResetQuery(unsigned int axisid);
        LinActBuf * getAxisHomeQuery(unsigned int axisid);
        LinActBuf * getAxisOnQuery(unsigned int axisid);
        LinActBuf * getAxisBrakeReleaseQuery(unsigned int axisid);

        int getPosition();

        unsigned int getStatus();

        unsigned int getGwStatus();

        LinActBuf * getBuffer();

        void send();
        LinActBuf * receiveStdin(int len);

        LinActBuf * pushByteRxBuffer(char c);

        int checkChecksum();

  };

}

#endif /* LINACT_H */
