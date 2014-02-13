#ifndef LINACTBUF_H
#define LINACTBUF_H

#include <cstdio>
#include <cstring>
#include <linactregdefs.h>
#include <linactbuf.h>

namespace IAI {

  class LinActBuf {
    unsigned char *ptr;
    public:
        LinActBuf();

        void push(unsigned char val);
        void reset();

        unsigned int len;
        unsigned char buf[LINACT_BUFLEN];
        char strbuf[LINACT_BUFLEN*2];
        void copy(LinActBuf *other);
        unsigned int crc_update(unsigned int crc,
                unsigned char a);
        void calc_crc();
        char *as_string();
        void readRegsisterStr(unsigned short startreg,
                unsigned short count);
        void writeRegisterStr(unsigned short reg,
                unsigned short value);
        void writeMultiRegisterStr(unsigned short reg,
            unsigned short reglen,
            unsigned char * data,
            unsigned char dlen);

  }; // End linactbuf class

}; // End namespace



#endif //~ end LINACTBUF_H
