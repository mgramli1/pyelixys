
#include <pylinact.h>

using namespace IAI;

LinActBuf* LinActBuf_new() {return new LinActBuf(); }

void LinActBuf_calc_crc(LinActBuf* buf) { buf->calc_crc(); };

char * LinActBuf_as_str(LinActBuf * buf) { return buf->as_string(); };

void LinActBuf_push(LinActBuf *buf, unsigned char val) { buf->push(val); }

void LinActBuf_reset(LinActBuf *buf) { buf->reset(); }

void LinActBuf_copy(LinActBuf * src, LinActBuf * dest) { dest->copy(src); }

unsigned int LinActBuf_len(LinActBuf * buf) {return buf->len;}

void LinActBuf_writeMultiRegister(LinActBuf * buf,
                                          unsigned short reg,
                                          unsigned short reglen,
                                          unsigned char * data,
                                          unsigned char len)
{
    buf->writeMultiRegisterStr(reg, reglen, data, len);
}


void LinActBuf_readRegsister(LinActBuf *buf,
        unsigned short reg,
        unsigned short count) {
    buf->readRegsisterStr(reg, count);
}

void LinActBuf_writeRegister(LinActBuf *buf,
        unsigned short reg,
        unsigned short value) {
    buf->writeRegisterStr(reg, value);
}

char * LinActBuf_buf(LinActBuf *buf) {
        return (char *)buf->buf;
}


LinearActuator * LinAct_new() { return new LinearActuator(); }


LinActBuf * LinAct_gatewayStatusQueury(LinearActuator *act) {
    return act->getGwStatusStr();
}

LinActBuf * LinAct_gatewayStartQuery(LinearActuator *act) {
    return act->getGwStartStr();
}

LinActBuf * LinAct_axisStatusQuery(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisStatus(axisid);
}

LinActBuf * LinAct_axisPosGetQuery(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisPos(axisid);
}

LinActBuf * LinAct_axisPosSetQuery(LinearActuator *act,
        unsigned int axisid, unsigned int pos) {
    return act->getSetAxisPos(axisid, pos);
}

LinActBuf * LinAct_axisStartQuery(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisStart(axisid);
}

LinActBuf * LinAct_axisPauseQuery(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisPause(axisid);
}

LinActBuf * LinAct_axisResetQuery(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisReset(axisid);
}

LinActBuf * LinAct_axisBrakeReleaseQuery(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisBrakeRelease(axisid);
}

LinActBuf * LinAct_axisHomeQuery(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisHome(axisid);
}

unsigned short LinAct_axisReadAddr(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisReadAddress(axisid);
}

unsigned short LinAct_axisWriteAddr(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisWriteAddress(axisid);
}




