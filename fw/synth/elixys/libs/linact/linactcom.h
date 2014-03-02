#ifndef _LINACTCOM_H_
#define _LINACTCOM_H_
#include "mbed.h"
#include "linact.hpp"
#include "pinmap.h"
#include "serial_api.h"


namespace IAI {
class LinearActuatorCom: public LinearActuator {
    public:
        LinearActuatorCom(PinName tx, PinName rx, PinName dir);
        Serial serial_;
        DigitalOut dir_;
        
        Timer timeout_timer;
        int timeout_ms;
        
        void waitTx();
        void writeChr(int c);
        void sendBuf(unsigned char *buf, int buflen);
        int readChr();
        void send();
        void setTimeout(int timeout);
        
        void readResponse();
        void readLen(int len);
        
        int sendAndRead(int retry=3);
        
        UARTName uartname;
        
};

}
#endif /* _LINACTCOM_H_ */