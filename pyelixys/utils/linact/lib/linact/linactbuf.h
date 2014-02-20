#ifndef LINACTBUF_H
#define LINACTBUF_H

#include <cstdio>
#include <cstring>
#include <linactregdefs.h>
#include <linactbuf.h>



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
