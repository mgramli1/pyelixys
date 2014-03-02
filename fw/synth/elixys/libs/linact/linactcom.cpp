#include "mbed.h"
#include "linactcom.h"


namespace IAI {

static const PinMap PinMap_UART_TX[] = {
    {P0_0,  UART_3, 2},
    {P0_2,  UART_0, 1},
    {P0_10, UART_2, 1},
    {P0_15, UART_1, 1},
    {P0_25, UART_3, 3},
    {P2_0 , UART_1, 2},
    {P2_8 , UART_2, 2},
    {P4_28, UART_3, 3},
    {NC   , NC    , 0}
};

static const PinMap PinMap_UART_RX[] = {
    {P0_1 , UART_3, 2},
    {P0_3 , UART_0, 1},
    {P0_11, UART_2, 1},
    {P0_16, UART_1, 1},
    {P0_26, UART_3, 3},
    {P2_1 , UART_1, 2},
    {P2_9 , UART_2, 2},
    {P4_29, UART_3, 3},
    {NC   , NC    , 0}
};


LinearActuatorCom::LinearActuatorCom(PinName tx, PinName rx, PinName dir): LinearActuator(), serial_(tx, rx), dir_(dir) {
    serial_.baud(230400);
    dir_ = 0;
    
    UARTName uart_tx = (UARTName)pinmap_peripheral(tx, PinMap_UART_TX);
    UARTName uart_rx = (UARTName)pinmap_peripheral(rx, PinMap_UART_RX);
    uartname = (UARTName)pinmap_merge(uart_tx, uart_rx);
    
    if ((int)uartname == NC) {
        error("Serial pinout mapping failed");
    }
}

void LinearActuatorCom::waitTx() {
    switch (uartname) {
        case UART_0: while (!(LPC_UART0->LSR & (1 << 6))); break;
        case UART_1: while (!(LPC_UART1->LSR & (1 << 6))); break;
        case UART_2: while (!(LPC_UART2->LSR & (1 << 6))); break;
        case UART_3: while (!(LPC_UART3->LSR & (1 << 6))); break;
    }
}

    
void LinearActuatorCom::writeChr(int c) {
    dir_ = 1;
    serial_.putc(c);
    waitTx();
    dir_ = 0;
    timeout_ms = 10;
}

void LinearActuatorCom::sendBuf(unsigned char *buf, int buflen) {
    dir_ = 1;
    for(int i=0; i<buflen; i++) {
        serial_.putc(*(buf+i));        
    } 
    waitTx();   
    dir_ = 0;
}

void LinearActuatorCom::send() {
    sendBuf(buffer.buf, buffer.len);
}

void LinearActuatorCom::setTimeout(int timeout) {
    timeout_ms = timeout;
}

void LinearActuatorCom::readLen(int len) {
    int c;
    for(int i=0;i<len;i++) {
        c = readChr();
        if (c > 0)
            pushByteRxBuffer((char)(0xFF&c));
    }
}

void LinearActuatorCom::readResponse() {
    readLen(buffer.exprxlen);
}

int LinearActuatorCom::readChr() {
   dir_ = 0;
   timeout_timer.reset();
   timeout_timer.start();
   while(timeout_timer.read_ms() < timeout_ms) {
        if(serial_.readable()) {
            timeout_timer.stop();
            timeout_timer.reset();
            return serial_.getc();
        }        
   }      
   timeout_timer.stop();
   timeout_timer.reset();
   return -1; 
}


int LinearActuatorCom::sendAndRead(int retry) {
    for(int i=0;i<retry;i++) {
        send();
        wait(0.01);
        readResponse();
        if (checkChecksum()) {
            return 0;
        }
    }
    return -1;
}

}