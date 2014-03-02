
#include <pylinact.h>

using namespace IAI;

LinActBuf* LinActBuf_new() {return new LinActBuf(); }

void LinActBuf_calc_crc(LinActBuf* buf) { buf->calc_crc(); };

char * LinActBuf_as_str(LinActBuf * buf) { return buf->as_string(); };

void LinActBuf_push(LinActBuf *buf, unsigned char val) { buf->push(val); }

void LinActBuf_pushRx(LinActBuf *buf, unsigned char val) { buf->pushRx(val); }

void LinActBuf_reset(LinActBuf *buf) { buf->reset(); }

void LinActBuf_copy(LinActBuf * src, LinActBuf * dest) { dest->copy(src); }

unsigned int LinActBuf_len(LinActBuf * buf) {return buf->len;}

unsigned int LinActBuf_rxlen(LinActBuf * buf) {return buf->rxlen;}

unsigned int LinActBuf_expected_rxlen(LinActBuf * buf) {return buf->exprxlen;}

unsigned int LinActBuf_rxdatalen(LinActBuf * buf) {return buf->datalen;}


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

char * LinActBuf_rxbuf(LinActBuf *buf) {
        return (char *)buf->rxbuf;
}

char * LinActBuf_payload(LinActBuf *buf) {
    return (char *)buf->rxdata();
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

LinActBuf * LinAct_axisTurnOnQuery(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisOn(axisid);
}

unsigned short LinAct_axisReadAddr(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisReadAddress(axisid);
}

unsigned short LinAct_axisWriteAddr(LinearActuator *act,
        unsigned int axisid) {
    return act->getAxisWriteAddress(axisid);
}

void LinAct_pushRx(LinearActuator *act,
        unsigned char c) {
    act->pushByteRxBuffer(c);
}

int LinAct_checkcrc(LinearActuator *act) {
    return act->checkChecksum();
}

LinActBuf *LinAct_getBuffer(LinearActuator *act) {
    return &(act->buffer);
}

float LinAct_getPosition(LinearActuator *act) {
    return act->getPosition();
}
