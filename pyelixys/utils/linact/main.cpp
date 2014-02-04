#include <stdio.h>
#include <linact.hpp>

using namespace IAI;
LinActBuf lbuf;


int main() {
    printf("Linear Actuator\r\n");
    lbuf.buf[0] = 0x3f;
    lbuf.buf[1] = 0x03;
    lbuf.buf[2] = 0xf7;
    lbuf.buf[3] = 0x00;
    lbuf.buf[4] = 0x00;
    lbuf.buf[5] = 0x02;
    lbuf.len = 6;
    lbuf.calc_crc();
    printf("%s\r\n", lbuf.as_string());
}
