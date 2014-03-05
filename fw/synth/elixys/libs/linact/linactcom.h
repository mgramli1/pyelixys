#ifndef _LINACTCOM_H_
#define _LINACTCOM_H_
#include "mbed.h"
#include "linact.hpp"
#include "pinmap.h"
#include "serial_api.h"


namespace IAI {
class LinearActuatorCom: public LinearActuator {
    public:
        LinearActuatorCom(PinName tx, PinName rx, PinName dir, PinName idir);
        Serial serial_;
        DigitalOut dir_;
        DigitalOut idir_;
        
        Timer timeout_timer;
        int timeout_ms;
        
        void enableRx();
        void enableTx();
        
        void clearRx();
        
        void waitTx();
        void writeChr(int c);
        void sendBuf(unsigned char *buf, int buflen);
        int readChr();
        void send();
        void setTimeout(int timeout);
        
        int readResponse();
        void readLen(int len);
        
        int sendAndRead();
        
        UARTName uartname;
        
};

}
#endif /* _LINACTCOM_H_ */