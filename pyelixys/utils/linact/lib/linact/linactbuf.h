#ifndef LINACTBUF_H
#define LINACTBUF_H

#include <cstdio>
#include <cstring>
#include <linactregdefs.h>


#if DBGLINACTBUF
#define LINBUFDBG(x, ...) std::printf("[LinActBuf:DBG]"x"\r\n", ##__VA_ARGS__);
#define LINBUFWARN(x, ...) std::printf("[LinActBuf:WARN]"x"\r\n", ##__VA_ARGS__);
#define LINBUFERR(x, ...) std::printf("[LinActBuf:ERR]"x"\r\n", ##__VA_ARGS__);
#else
#define LINBUFDBG(x, ...)
#define LINBUFWARN(x, ...)
#define LINBUFERR(x, ...)
#endif

#define LINBUFINFO(x, ...) std::printf("[LinActBuf:INFO]"x"\r\n", ##__VA_ARGS__);

namespace IAI {

  const int RXMSGLENERR= -2;
  const int RXINVALIDCRCERR = -1;
  const int RXWRCRCOK = 1;
  const int RXMULWRCRCOK = 2;
  const int RXREADCRCOK = 3;

  const int GWADDRPOS = 0;
  const int CMDPOS = 1;

  class  LinActBuf {

    unsigned char *ptr;
    unsigned char *rxptr;
    unsigned char *rxmsgptr;
    public:
        LinActBuf();

        void push(unsigned char val);
        void pushRx(unsigned char val);
        void reset();
        void resetRx();

        unsigned int len;
        unsigned int rxlen;
        unsigned int exprxlen;
        unsigned int datalen;

        unsigned char buf[LINACT_BUFLEN];
        unsigned char rxbuf[LINACT_BUFLEN];
        char strbuf[LINACT_BUFLEN*2];
        char rxstrbuf[LINACT_BUFLEN*2];
        void copy(LinActBuf *other);
        unsigned int crc_update(unsigned int crc,
                unsigned char a);
        void calc_crc();
        char *as_string();
        char *rx_as_string();
        void readRegsisterStr(unsigned short startreg,
                unsigned short count);
        void writeRegisterStr(unsigned short reg,
                unsigned short value);
        void writeMultiRegisterStr(unsigned short reg,
            unsigned short reglen,
            unsigned char * data,
            unsigned char dlen);

        unsigned char * rxdata();
        unsigned int rxdatalen();
        int rxvalidate();
        int checkrxcrc();

  }; // End linactbuf class

}; // End namespace

#endif //~ end LINACTBUF_H
