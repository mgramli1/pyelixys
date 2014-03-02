#include "mbed.h"
#include "mcp3202.h"

using namespace mbed;

MCP3202::MCP3202(SPI &spi, void(*sel)(void), void(*usel)(void)): _spi(spi) {    
    selectfxn = sel;
    unselectfxn = usel;     
    enable();    
}

MCP3202::~MCP3202() {
}

int MCP3202::readA(){
    //printf("Read A\r\n");
    select();
    _spi.write(STARTBIT);
    int upperbyte = _spi.write(SGL_DIFF|MSBF);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

int MCP3202::readB(){
    //printf("Read B\r\n");
    select();
    _spi.write(STARTBIT);
    int upperbyte = _spi.write(SGL_DIFF|ODD_SIGN|MSBF);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

void MCP3202::disable() {
    bshutdown = true;       
}

void MCP3202::enable() {
    bshutdown = false;
}

void MCP3202::configspi() {
    _spi.format(8, 0);
    //_spi.frequency();
}

void MCP3202::sendValue(int value) {    
    select();
    _spi.write(value);    
    deselect();
}

void MCP3202::select() {
    //Set CS low to start transmission (interrupts conversion)   
    configspi(); 
    selectfxn();
}

void MCP3202::deselect() {
    //Set CS high to stop transmission (restarts conversion)    
    unselectfxn();    
}