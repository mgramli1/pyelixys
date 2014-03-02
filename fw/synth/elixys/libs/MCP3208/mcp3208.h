#include "mbed.h"
#include "bit.h"
#ifndef MCP3208_H
#define MCP3208_H

#define MCP3208_STARTBIT        BIT(2)
#define MCP3208_SGL_DIFF        BIT(1)
#define MCP3208_ADCSEL2         BIT(0)
#define MCP3208_ADCSEL1         BIT(7)
#define MCP3208_ADCSEL0         BIT(6)

#define USELECTADC0      (MCP3208_STARTBIT|MCP3208_SGL_DIFF)
#define LSELECTADC0      (0)

#define USELECTADC1      (MCP3208_STARTBIT|MCP3208_SGL_DIFF)
#define LSELECTADC1      (MCP3208_ADCSEL0)

#define USELECTADC2      (MCP3208_STARTBIT|MCP3208_SGL_DIFF)
#define LSELECTADC2      (MCP3208_ADCSEL1)

#define USELECTADC3      (MCP3208_STARTBIT|MCP3208_SGL_DIFF)
#define LSELECTADC3      (MCP3208_ADCSEL1|MCP3208_ADCSEL0)

#define USELECTADC4      (MCP3208_STARTBIT|MCP3208_SGL_DIFF|MCP3208_ADCSEL2)
#define LSELECTADC4      (0)

#define USELECTADC5      (MCP3208_STARTBIT|MCP3208_SGL_DIFF|MCP3208_ADCSEL2)
#define LSELECTADC5      (MCP3208_ADCSEL0)

#define USELECTADC6      (MCP3208_STARTBIT|MCP3208_SGL_DIFF|MCP3208_ADCSEL2)
#define LSELECTADC6      (MCP3208_ADCSEL1)

#define USELECTADC7      (MCP3208_STARTBIT|MCP3208_SGL_DIFF|MCP3208_ADCSEL2)
#define LSELECTADC7      (MCP3208_ADCSEL1|MCP3208_ADCSEL0)


// BITS 0-11 set the output voltage!!!

class mcp3208 {
public:

/*
* Constructor
*/
mcp3208(SPI &spi, void(*sel)(void), void(*usel)(void));

/*
* Destructor
*/
~mcp3208();

/*
* Write to DAC 0
*/
int read0();


/*
* Write to DAC 1
*/
int read1();

/*
* Write to DAC 2
*/
int read2();

/*
* Write to DAC 3
*/
int read3();

/*
* Write to DAC 4
*/
int read4();

/*
* Write to DAC 5
*/
int read5();

/*
* Write to DAC 6
*/
int read6();

/*
* Write to DAC 7
*/
int read7();

/*
* Select the ADC for data retrievel
*/
void select();

/*
* Deselect the ADC
*/
void deselect();

private:

// These function pointer allows you to
// use a routine to control the chip select line
// important for me since all of my chip select lines are
// controlled by a array of shift registers!
void(*selectfxn)(void);
void(*unselectfxn)(void);
SPI &_spi;

// Configure the SPI periphreal to drive our ADCs
void configspi();
}; // end class MCP3208

#endif //MCP3208_H