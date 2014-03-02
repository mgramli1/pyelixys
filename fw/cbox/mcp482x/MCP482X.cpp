#include "mbed.h"
#include "MCP482X.h"

using namespace mbed;

MCP482X::MCP482X(SPI &spi, DigitalOut &cspin): _spi(spi), _cspin(cspin) {
    gainA = 1;
    gainB = 1;
    valA = 0;
    valB = 0;     
    enable();
    _cspin.write(1);
}

MCP482X::~MCP482X() {
}

int MCP482X::writeA(int value){
    int tempval = 0;
    valA = (value & 0x0FFF);
    tempval = SELECTDACA(valA);
    
    if(gainA == 1) {
        tempval = SELECT1XGAIN(tempval);           
    } else {
        tempval = SELECT2XGAIN(tempval);        
    }
    
    if(bshutdown==true) {
        tempval = SELECTPWROFF(tempval);
    } else {
        tempval = SELECTPWRON(tempval);
    }
    
    sendValue(tempval);
    return tempval;
}

int MCP482X::writeB(int value){

    int tempval = 0;
    valB = (value & 0x0FFF);
    tempval = SELECTDACB(valB);
    
    if(gainB == 1) {
        tempval = SELECT1XGAIN(tempval);           
    } else {
        tempval = SELECT2XGAIN(tempval);        
    }
    
    if(bshutdown==true) {
        tempval = SELECTPWROFF(tempval);
    } else {
        tempval = SELECTPWRON(tempval);
    }
    
    sendValue(tempval);
    return tempval;
}

void MCP482X::setGainA(int value){
    if(value==1 || value == 2)
        gainA = value;
    else
        gainA = 1;
}

void MCP482X::setGainB(int value){
    if(value==1 || value == 2)
        gainB = value;
    else
        gainB = 1;
}

void MCP482X::disable() {
    bshutdown = true;
    writeA(valA);
    writeB(valB);        
}

void MCP482X::enable() {
    bshutdown = false;
    writeA(valA);
    writeB(valB);
}

void MCP482X::configspi() {
    _spi.format(16, 0);
    _spi.frequency(50000);
}

void MCP482X::sendValue(int value) {
    configspi();
    _cspin.write(0);
    _spi.write(value);    
    _cspin.write(1);
}