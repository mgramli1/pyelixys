#include <stdio.h>
#include <string.h>
#include <linact.hpp>



namespace IAI {


LinActBuf::LinActBuf() {
    reset();
}

void LinActBuf::push(unsigned char value) {
    len++;
    *ptr = value;
    ptr++;
}

void LinActBuf::reset() {
    len = 0;
    ptr = buf;
    buf[0] = GWADDR;
}


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

void LinActBuf::readRegsisterStr(unsigned short startreg, unsigned short count) {
    buf[0] = GWADDR;
    buf[1] = LINACT_READ_MULTI;
    buf[2] = (unsigned char)((startreg & 0xFF00) >> 8);
    buf[3] = (unsigned char)(startreg & 0x00FF);
    buf[4] = (unsigned char)((count & 0xFF00) >> 8);
    buf[5] = (unsigned char)(count & 0x00FF);
    len = 6;
    calc_crc();
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
}

LinActBuf * LinearActuator::getGwStatusStr() {
  //gwstatus = "\x3f\x03\xf7\x00\x00\x02"
  buffer.readRegsisterStr(LINACT_GWSTATUS0, 2);
  return &buffer;
}


LinActBuf * LinearActuator::getGwStartStr() {
  //alwayson = "\x3f\x06\xf6\x00\x80\x00"
  // The 15-bit of the GWCTRL register must be set
  // to enable applicable control, page 163 from
  // ROBONET(ME0208-13A-A).pdf
  buffer.writeRegisterStr(GWCTRL0, GWCTRL_APP_SIG);
  return &buffer;
}


unsigned short LinearActuator::getAxisReadAddress(unsigned int axisid) {

  switch(axisid) {
    case 0:
      return AXIS0_BASE_RD;
    case 1:
      return AXIS1_BASE_RD;
    case 2:
      return AXIS2_BASE_RD;
    case 3:
      return AXIS3_BASE_RD;
    case 4:
      return AXIS4_BASE_RD;
    default:
      return 0;
  }
}

unsigned short LinearActuator::getAxisWriteAddress(unsigned int axisid) {

  switch(axisid) {
    case 0:
      return AXIS0_BASE_WR;
    case 1:
      return AXIS1_BASE_WR;
    case 2:
      return AXIS2_BASE_WR;
    case 3:
      return AXIS3_BASE_WR;
    case 4:
      return AXIS4_BASE_WR;
    default:
      return 0;
  }
}

LinActBuf * LinearActuator::getAxisStatus(unsigned int axisid) {
//axis1alarm = "\x3f\x03\xf7\x12\x00\x01"
    unsigned short axis_temp_reg;
    axis_temp_reg = getAxisReadAddress(axisid) + STATUS_SIG_OFFSET;
    buffer.readRegsisterStr(axis_temp_reg, 1);
    return &buffer;
}

LinActBuf * LinearActuator::getAxisPos(unsigned int axisid) {
    unsigned short axis_temp_reg;
    axis_temp_reg = getAxisReadAddress(axisid) + POS_SET_LO_OFFSET;
    buffer.readRegsisterStr(axis_temp_reg, 2); // Read 2 to get lo and hi
    return &buffer;
}

LinActBuf * LinearActuator::getSetAxisPos(unsigned int axisid, unsigned int position) {
    unsigned short axis_temp_reg;
    LinActBuf temp;
    axis_temp_reg = getAxisWriteAddress(axisid) + POS_SET_LO_OFFSET;
    temp.buf[2] = (unsigned char)((position & 0xFF000000) >> 24);
    temp.buf[3] = (unsigned char)((position & 0x00FF0000) >> 16);
    temp.buf[0] = (unsigned char)((position & 0x0000FF00) >> 8);
    temp.buf[1] = (unsigned char)((position & 0x000000FF));
    temp.len = 4;
    buffer.writeMultiRegisterStr(axis_temp_reg, 2, temp.buf, temp.len);
    return &buffer;
}


LinActBuf * LinearActuator::getAxisStart(unsigned int axisid) {
    //startcmd0 = "\x3f\x06\xf6\x0b\x00\x11"
    unsigned short int axisreg;
    unsigned short value;
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_SON|AXIS_CTRL_CSTR);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

LinActBuf * LinearActuator::getAxisPause(unsigned int axisid) {
    //pausecmd = "\x3f\x06\xf6\x0b\x00\x14"
    unsigned short int axisreg;
    unsigned short value;
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_SON|AXIS_CTRL_STP);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

LinActBuf * LinearActuator::getAxisReset(unsigned int axisid) {
    // resetcmd0 = "\x3f\x06\xf6\x0b\x00\x08"
    unsigned short int axisreg;
    unsigned short value;
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_RES);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

LinActBuf * LinearActuator::getAxisBrakeRelease(unsigned int axisid) {
    unsigned short int axisreg;
    unsigned short value;
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_BKRL);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

void LinearActuator::send() {
    // Drive WR pin
    for(int i=0;i<buffer.len;i++){
        putchar(buffer.buf[i]);
    }
    // Stop driving WR pin to receive
}

LinActBuf * LinearActuator::receive(int len) {
    // Fill buffer
    inbuf.reset();
    for(int i=0;i<len;i++) {
        inbuf.push(getc(stdin));
        //printf("Inbuf.len=%d", inbuf.len);
    }
    printf("Receive: %s\r\n", inbuf.as_string());
}

} // End Namespace IAI
