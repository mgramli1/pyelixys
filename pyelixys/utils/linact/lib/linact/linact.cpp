#include <stdio.h>
#include <string.h>
#include <linact.hpp>



namespace IAI {


LinearActuator::LinearActuator() {
}

LinearActuator::~LinearActuator() {
}

LinActBuf * LinearActuator::getGwStatusStr() {
  //gwstatus = "\x3f\x03\xf7\x00\x00\x02"

  buffer.reset();
  buffer.readRegsisterStr(LINACT_GWSTATUS0, 2);
  return &buffer;
}


LinActBuf * LinearActuator::getGwStartStr() {
  //alwayson = "\x3f\x06\xf6\x00\x80\x00"
  // The 15-bit of the GWCTRL register must be set
  // to enable applicable control, page 163 from
  // ROBONET(ME0208-13A-A).pdf
  buffer.reset();
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
    buffer.reset();
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
    buffer.reset();
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
    buffer.reset();
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_SON|AXIS_CTRL_CSTR);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

LinActBuf * LinearActuator::getAxisPause(unsigned int axisid) {
    //pausecmd = "\x3f\x06\xf6\x0b\x00\x14"
    unsigned short int axisreg;
    unsigned short value;
    buffer.reset();
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_SON|AXIS_CTRL_STP);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

LinActBuf * LinearActuator::getAxisReset(unsigned int axisid) {
    // resetcmd0 = "\x3f\x06\xf6\x0b\x00\x08"
    unsigned short int axisreg;
    unsigned short value;
    buffer.reset();
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_RES);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

LinActBuf * LinearActuator::getAxisHome(unsigned int axisid) {
    // resetcmd0 = "\x3f\x06\xf6\x0b\x00\x08"
    unsigned short int axisreg;
    unsigned short value;
    buffer.reset();
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_HOME|AXIS_CTRL_SON);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

LinActBuf * LinearActuator::getAxisOn(unsigned int axisid) {
    // resetcmd0 = "\x3f\x06\xf6\x0b\x00\x08"
    unsigned short int axisreg;
    unsigned short value;
    buffer.reset();
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_SON);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

LinActBuf * LinearActuator::getAxisBrakeRelease(unsigned int axisid) {
    unsigned short int axisreg;
    unsigned short value;
    buffer.reset();
    axisreg = getAxisWriteAddress(axisid) + CNTRL_SIG_OFFSET;
    value = (AXIS_CTRL_BKRL);
    buffer.writeRegisterStr(axisreg, value);
    return &buffer;
}

float LinearActuator::getPosition() {
    long current_pos;
    unsigned char *payload;
    short slo = 0;
    short shi = 0;
    int payloadlen = 0;

    if(buffer.rxdata()==0 || checkChecksum() < 0)
        return NOTPOSMSGERR;

    payload = buffer.rxdata();
    payloadlen = buffer.rxdatalen();

    if(buffer.rxdatalen()!=4)
        return NOTPOSMSGERR;

    current_pos = (payload[1]<<0)+(payload[0]<<8) +
        ((payload[2] & 0x7F)<<24)+(payload[3] <<16);

    if(0x80 & payload[2]) {
        // Check if we need to flip our sign
        //printf("Negative\r\n");
        current_pos = current_pos * -1;
    }

    return (float) (current_pos / 100.0);

}

LinActBuf * LinearActuator::getBuffer() {
    return &buffer;
}

void LinearActuator::send() {
    // Drive WR pin
    for(int i=0;i<buffer.len;i++){
        putchar(buffer.buf[i]);
    }
    // Stop driving WR pin to receive
}

LinActBuf * LinearActuator::receiveStdin(int len) {
    // Fill buffer
    for(int i=0;i<len;i++) {
        pushByteRxBuffer(getc(stdin));
        //printf("Inbuf.len=%d", rxbuf.len);
    }
    LINACTINFO("Receive: %s\r\n", buffer.rx_as_string());
}

LinActBuf * LinearActuator::pushByteRxBuffer(char c) {
    buffer.pushRx(c);
    return &buffer;
}

int LinearActuator::checkChecksum() {
    return buffer.rxvalidate();
}

} // End Namespace IAI
