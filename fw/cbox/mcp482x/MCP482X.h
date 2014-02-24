#include "mbed.h"
#include "bit.h"
#ifndef MCP482X_H
#define MCP482X_H

#define MCP482X_VREF 2048

#define DACSELBIT       BIT(15)
#define DACUNDEF        BIT(14)
#define GAINBIT         BIT(13)
#define SHDNBIT         BIT(12)

#define SELECTDACA(VALUE)        CLEARBITS(VALUE,DACSELBIT)
#define SELECTDACB(VALUE)        SETBITS(VALUE,DACSELBIT)
#define SELECT1XGAIN(VALUE)      SETBITS(VALUE,GAINBIT)
#define SELECT2XGAIN(VALUE)      CLEARBITS(VALUE,GAINBIT)
#define SELECTPWRON(VALUE)       SETBITS(VALUE, SHDNBIT)
#define SELECTPWROFF(VALUE)      CLEARBITS(VALUE, SHDNBIT)

// BITS 0-11 set the output voltage!!!

class MCP482X {
public:

/*
* Constructor
*/
MCP482X(SPI &spi, DigitalOut &cspin);

/*
* Destructor
*/
~MCP482X();

/*
* Write to DAC A
*/
int writeA(int value);


/*
* Write to DAC B
*/
int writeB(int value);


/*
* Set Gain for DAC A 1 or 2
*/
void setGainA(int value);


/*
* Set Gain for DAC B 1 or 2
*/
void setGainB(int value);

/*
* Shutdown DAC
*/
void disable();

/*
* Power On DAC
*/
void enable();

private:

int gainA;
int gainB;
int valA;
int valB;    
bool bshutdown;
SPI &_spi;
DigitalOut &_cspin;

void configspi();
void sendValue(int value);
}; // end class MCP482X

#endif //MCP482X_H