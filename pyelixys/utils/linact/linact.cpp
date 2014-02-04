#include <stdio.h>
#include <string.h>
#include <linact.hpp>



namespace IAI {
char linactbuf[LINACT_BUFLEN];

void LinActBuf::copy(LinActBuf &other) {
    for(int i=0;i<other.len;i++) {
        buf[i] = other.buf[i];
    }
}


LinearActuator::LinearActuator() {
}

LinearActuator::~LinearActuator() {
}

unsigned int LinActBuf::crc_update(unsigned int crc, unsigned char a) {
    crc ^= a;
    printf("CRC^=a:0x%x, a=%x\r\n", crc, a);
    for(int i=0;i<8;i++) {
        if(crc & 1) {
            crc = (crc >> 1) ^ 0xA001;
        } else {
            crc = crc >> 1;
        }
    }
    printf("return CRC: 0x%x\r\n", crc);
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
    printf("0x%04X\r\n", crc);
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
        printf("%d:%s\r\n",i, tmpbuf);
    }
    return strbuf;
}


}
