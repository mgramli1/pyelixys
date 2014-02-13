
#include <pylinact.h>

using namespace IAI;

LinActBuf* LinActBuf_new() {return new LinActBuf(); }

void LinActBuf_calc_crc(LinActBuf* buf) { buf->calc_crc(); };

char * LinActBuf_as_str(LinActBuf * buf) { return buf->as_string(); };

void LinActBuf_push(LinActBuf *buf, unsigned char val) { buf->push(val); }

void LinActBuf_reset(LinActBuf *buf) { buf->reset(); }

void LinActBuf_copy(LinActBuf * src, LinActBuf * dest) { dest->copy(src); }
