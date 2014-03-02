#include "mbed.h"
#include "mcp482x.h"

using namespace mbed;

MCP482X::MCP482X(SPI &spi, void(*sel)(void), void(*usel)(void)): _spi(spi) {
    gainA = 1;
    gainB = 1;
    valA = 0;
    valB = 0;
    selectfxn = sel;
    unselectfxn = usel;     
    enable();    
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
    //_spi.frequency();
}

void MCP482X::sendValue(int value) {    
    select();
    _spi.write(value);    
    deselect();
}

void MCP482X::select() {
    //Set CS low to start transmission (interrupts conversion)   
    configspi(); 
    selectfxn();
}

void MCP482X::deselect() {
    //Set CS high to stop transmission (restarts conversion)    
    unselectfxn();    
}