#include "mbed.h"
#include "mcp3208.h"

using namespace mbed;

mcp3208::mcp3208(SPI &spi, void(*sel)(void), void(*usel)(void)): _spi(spi) {    
    selectfxn = sel;
    unselectfxn = usel;         
}

mcp3208::~mcp3208() {
}

int mcp3208::read0(){
    //printf("Read 0\r\n");
    select();
    _spi.write(USELECTADC0);
    int upperbyte = _spi.write(LSELECTADC0);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

int mcp3208::read1(){
    //printf("Read 1\r\n");
    select();
    _spi.write(USELECTADC1);
    int upperbyte = _spi.write(LSELECTADC1);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

int mcp3208::read2(){
    //printf("Read 2\r\n");
    select();
    _spi.write(USELECTADC2);
    int upperbyte = _spi.write(LSELECTADC2);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

int mcp3208::read3(){
    //printf("Read 3\r\n");
    select();
    _spi.write(USELECTADC3);
    int upperbyte = _spi.write(LSELECTADC3);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

int mcp3208::read4(){
    //printf("Read 4\r\n");
    select();
    _spi.write(USELECTADC4);
    int upperbyte = _spi.write(LSELECTADC4);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

int mcp3208::read5(){
    //printf("Read 5\r\n");
    select();
    _spi.write(USELECTADC5);
    int upperbyte = _spi.write(LSELECTADC5);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

int mcp3208::read6(){
    //printf("Read 6\r\n");
    select();
    _spi.write(USELECTADC6);
    int upperbyte = _spi.write(LSELECTADC6);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

int mcp3208::read7(){
    //printf("Read 7\r\n");
    select();
    _spi.write(USELECTADC7);
    int upperbyte = _spi.write(LSELECTADC7);
    int lowerbyte = _spi.write(0x00);
    deselect();
    int value = ((0x0F & upperbyte) << 8) | lowerbyte;
    return value;
}

void mcp3208::configspi() {
    _spi.format(8, 0);
    //_spi.frequency();
}

void mcp3208::select() {
    //Set CS low to start transmission (interrupts conversion)   
    configspi(); 
    selectfxn();
}

void mcp3208::deselect() {
    //Set CS high to stop transmission (restarts conversion)    
    unselectfxn();    
}