#include <linactbuf.h>


namespace IAI {

LinActBuf::LinActBuf() {
    reset();
}

void LinActBuf::push(unsigned char value) {
    len++;
    *ptr = value;
    ptr++;
}

void LinActBuf::pushRx(unsigned char value) {
    rxlen++;
    *rxptr = value;
    rxptr++;
}

void LinActBuf::reset() {
    len = 0;
    rxlen = 0;
    exprxlen = 0;
    ptr = buf;
    buf[0] = GWADDR;
    rxptr = rxbuf;
    rxbuf[0] = 0;
    rxmsgptr = 0;
}


void LinActBuf::copy(LinActBuf *other) {
    for(int i=0;i<other->len;i++) {
        buf[i] = other->buf[i];
    }
}

unsigned int LinActBuf::crc_update(unsigned int crc, unsigned char a) {
    crc ^= a;
    //printf("CRC^=a:0x%x, a=%x\r\n", crc, a);
    for(int i=0;i<8;i++) {
        if(crc & 1) {
            crc = (crc >> 1) ^ 0xA001;
        } else {
            crc = crc >> 1;
        }
    }
    //printf("return CRC: 0x%x\r\n", crc);
    return crc;
}

void LinActBuf::calc_crc() {

    unsigned short crc = 0xFFFF;

    for(int i=0;i<len;i++) {
        crc = crc_update(crc, buf[i]);
    }

    if (len+2 > LINACT_BUFLEN) {
        // This is an ERROR so log it
        printf("Tried to write beyond buffer length\n");
        return;
    }
    //printf("0x%04X\r\n", crc);
    buf[len] = (crc & 0xFF);
    buf[len+1] = ((crc & 0xFF00) >> 8);
    len=len+2;
}

char * LinActBuf::as_string() {
    strbuf[0]='\0';
    char tmpbuf[4] = "";
    for(int i=0;i<len;i++) {
        sprintf(tmpbuf, "%02X", (unsigned char)buf[i]);

        strcat(strbuf,tmpbuf);
        //printf("%d:%s\r\n",i, tmpbuf);
    }
    return strbuf;
}

char * LinActBuf::rx_as_string() {
    rxstrbuf[0]='\0';
    char tmpbuf[4] = "";
    for(int i=0;i<len;i++) {
        sprintf(tmpbuf, "%02X", (unsigned char)buf[i]);

        strcat(rxstrbuf,tmpbuf);
        //printf("%d:%s\r\n",i, tmpbuf);
    }
    return rxstrbuf;
}

void LinActBuf::readRegsisterStr(unsigned short startreg, unsigned short count) {
    buf[0] = GWADDR;
    buf[1] = LINACT_READ_MULTI;
    buf[2] = (unsigned char)((startreg & 0xFF00) >> 8);
    buf[3] = (unsigned char)(startreg & 0x00FF);
    buf[4] = (unsigned char)((count & 0xFF00) >> 8);
    buf[5] = (unsigned char)(count & 0x00FF);
    len = 6;
    calc_crc();

    // See page 151
    // Header + crc + 2*numreg
    datalen = 2 * count;
    exprxlen = 5 + datalen; // Len in bytes

    rxmsgptr = rxbuf + 3;
}

void LinActBuf::writeRegisterStr(unsigned short reg, unsigned short value) {
    buf[0] = GWADDR;
    buf[1] = LINACT_WRITE;
    buf[2] = (unsigned char)((reg & 0xFF00) >> 8);
    buf[3] = (unsigned char)(reg & 0x00FF);
    buf[4] = (unsigned char)((value & 0xFF00) >>8);
    buf[5] = (unsigned char)(value & 0x00FF);
    len = 6;
    calc_crc();

    // See Page 163 for expected len
    exprxlen = 8; //Len in bytes
}

void LinActBuf::writeMultiRegisterStr(unsigned short reg,
    unsigned short reglen, unsigned char * data, unsigned char dlen) {

    buf[0] = GWADDR;
    buf[1] = LINACT_WRITE_MULTI;
    buf[2] = (unsigned char)((reg & 0xFF00) >> 8);
    buf[3] = (unsigned char)(reg & 0x00FF);
    buf[4] = (unsigned char)((reglen & 0xFF00) >> 8);
    buf[5] = (unsigned char)(reglen & 0x00FF);
    buf[6] = dlen;


    for(int i=0;i<dlen;i++) {
        buf[7+i] = data[i];
    }
    len = dlen+7;
    calc_crc();

    // See page 180
    exprxlen = 8; // Len in bytes

}


unsigned char * LinActBuf::rxdata() {
    return rxmsgptr;
}

unsigned int LinActBuf::rxdatalen() {
    return datalen;
}

// Check the checksum
int LinActBuf::rxvalidate() {
        if((buf[len-1] == rxbuf[rxlen-1]) &&
                (buf[len-2] == rxbuf[rxlen-2]))
            return 1;
        else
            return 0;
}

} // End IAI Namespace


