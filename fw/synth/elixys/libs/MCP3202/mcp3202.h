#include "mbed.h"
#include "bit.h"
#ifndef MCP3202_H
#define MCP3202_H

#define MCP482X_VREF 2048

#define STARTBIT    BIT(0)
#define SGL_DIFF    BIT(7)
#define ODD_SIGN    BIT(6)
#define MSBF        BIT(5)

#define SELECTSTART(VALUE)       SETBITS(VALUE,STARTBIT)
#define SELECTDACB(VALUE)        SETBITS(VALUE,DACSELBIT)
#define SELECT1XGAIN(VALUE)      SETBITS(VALUE,GAINBIT)
#define SELECT2XGAIN(VALUE)      CLEARBITS(VALUE,GAINBIT)
#define SELECTPWRON(VALUE)       SETBITS(VALUE, SHDNBIT)
#define SELECTPWROFF(VALUE)      CLEARBITS(VALUE, SHDNBIT)

// BITS 0-11 set the output voltage!!!

class MCP3202 {
public:

/*
* Constructor
*/
MCP3202(SPI &spi, void(*sel)(void), void(*usel)(void));

/*
* Destructor
*/
~MCP3202();

/*
* Write to DAC A
*/
int readA();


/*
* Write to DAC B
*/
int readB();

/*
* Shutdown DAC
*/
void disable();

/*
* Power On DAC
*/
void enable();

void select();

void deselect();

private:

void(*selectfxn)(void);
void(*unselectfxn)(void);
bool bshutdown;
SPI &_spi;

void configspi();
void sendValue(int value);
}; // end class MCP3202

#endif //MCP3202_H