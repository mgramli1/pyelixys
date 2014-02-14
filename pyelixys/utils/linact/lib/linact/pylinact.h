
#ifndef PYLINACT_H
#define PYLINACT_H

#include <linactbuf.h>
#include <linact.hpp>

#ifdef BUILD_DLL
// Export DLL
#define EXPORT_DLL __declspec(dllexport)
#else
#define EXPORT_DLL __declspec(dllimport)
#endif

using namespace IAI;

extern "C" {


LinActBuf* LinActBuf_new();
void LinActBuf_push(LinActBuf *buf, unsigned char c);

void LinActBuf_calc_crc(LinActBuf* buf);

char * LinActBuf_as_str(LinActBuf * buf);

void LinActBuf_push(LinActBuf *buf, unsigned char val);

void LinActBuf_reset(LinActBuf *buf);

void LinActBuf_copy(LinActBuf * src, LinActBuf * dest);

unsigned int LinActBuf_len(LinActBuf * buf);

void LinActBuf_readRegsister(LinActBuf *buf,
        unsigned short reg,
        unsigned short count);

void LinActBuf_writeRegister(LinActBuf *buf,
        unsigned short reg,
        unsigned short value);

void LinActBuf_writeMultiRegister(LinActBuf * buf,
        unsigned short reg,
        unsigned short reglen,
        unsigned char * data,
        unsigned char len);

char * LinActBuf_buf(LinActBuf* buf);


LinearActuator* LinAct_new();

LinActBuf * LinAct_gatewayStatusQueury(LinearActuator *act);

LinActBuf * LinAct_gatewayStartQuery(LinearActuator *act);

LinActBuf * LinAct_axisStatusQuery(LinearActuator *act,
        unsigned int axisid);

LinActBuf * LinAct_axisPosSetQuery(LinearActuator *act,
        unsigned int axisid,
        unsigned int pos);

LinActBuf * LinAct_axisPosGetQuery(LinearActuator *act,
        unsigned int axisid);

LinActBuf * LinAct_axisStartQuery(LinearActuator *act,
        unsigned int axisid);

LinActBuf * LinAct_axisPauseQuery(LinearActuator *act,
        unsigned int axisid);

LinActBuf * LinAct_axisResetQuery(LinearActuator *act,
        unsigned int axisid);

LinActBuf * LinAct_axisBrakeReleaseQuery(LinearActuator *act,
        unsigned int axisid);

LinActBuf * LinAct_axisHomeQuery(LinearActuator *act,
        unsigned int axisid);

unsigned short LinAct_axisWriteAddr(LinearActuator *act,
        unsigned int axisid);

unsigned short LinAct_axisReadAddr(LinearActuator *act,
        unsigned int axisid);

}

#endif
