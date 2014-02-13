
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
}

#endif
