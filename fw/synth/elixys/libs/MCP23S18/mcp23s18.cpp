#include "mbed.h"
#include "mcp23s18.h"

mcp23s18::mcp23s18(SPI& _spi, void(*sel)(void), void(*usel)(void)) : spi(_spi) {
    selectfxn = sel;
    unselectfxn = usel;    
}


void mcp23s18::configspi() {
    spi.format(8, 0);
    //_spi.frequency();
}

void mcp23s18::select() {
    //Set CS low to start transmission (interrupts conversion) 
    configspi();   
    selectfxn();
}

void mcp23s18::deselect() {
    //Set CS high to stop transmission (restarts conversion)    
    unselectfxn();    
}

int mcp23s18::initialize(int setType) {  
    int ret;  
    select();
    spi.write(MCP23S18WRADDR);
    spi.write(IOCONA_BANK0);
    spi.write(IOCON_MIRROR|IOCON_SEQOP);
    deselect();
    select();
    spi.write(MCP23S18RDADDR);
    spi.write(IOCONA_BANK0);
    ret = spi.write(IOCONA_BANK0);
    deselect();
    ret = read_register(IOCONA_BANK0);
    //printf("GO away Init MCP23S18 0x%x\r\n", ret);                
    faultCode=0;
    return ret;
}

int mcp23s18::read_config() {
    int ret = read_register(IOCONA_BANK0);      
    return ret;
}

void mcp23s18::set_direction(unsigned int dirpins) {
    select();
    spi.write(MCP23S18WRADDR);
    spi.write(IODIRA_BANK0);
    spi.write(0x000000FF & dirpins);
    deselect();
    select();    
    spi.write(MCP23S18WRADDR);
    spi.write(IODIRB_BANK0);
    spi.write(0x000000FF & (dirpins>>8));    
    deselect();
}

int mcp23s18::read_direction() {
    select();
    spi.write(MCP23S18RDADDR);
    spi.write(IODIRA_BANK0);   
    int lower_byte = spi.write(IODIRB_BANK0);
    int upper_byte = spi.write(IODIRA_BANK0);       
    deselect();    
    int val = lower_byte|(upper_byte << 8);
    return val;
}

void mcp23s18::set_all_output() {
    set_direction(IOX_ALLOUTPUT);
}


void mcp23s18::set_all_input() {
    set_direction(IOX_ALLINPUT);
}

    
void mcp23s18::set_inverted(unsigned int invpins) {
    select();
    spi.write(MCP23S18WRADDR);
    spi.write(IPOLA_BANK0);
    spi.write(0x000000FF & invpins);
    deselect();
    select();    
    spi.write(MCP23S18WRADDR);
    spi.write(IPOLB_BANK0);
    spi.write(0x000000FF & (invpins>>8));    
    deselect();
}

int mcp23s18::read_register(char reg) {
    select();
    spi.write(MCP23S18RDADDR);
    spi.write(reg);
    int ret = spi.write(reg);    
    deselect();
    return ret;
}

int mcp23s18::read_port() {    
    select();
    spi.write(MCP23S18RDADDR);
    spi.write(GPIOA_BANK0);   
    int lower_byte = spi.write(GPIOB_BANK0);
    int upper_byte = spi.write(GPIOA_BANK0);       
    deselect();    
    int val = lower_byte|(upper_byte << 8);
    return val;
}

int mcp23s18::read_latch() {    
    select();
    spi.write(MCP23S18RDADDR);
    spi.write(OLATA_BANK0);   
    int lower_byte = spi.write(OLATB_BANK0);
    int upper_byte = spi.write(OLATA_BANK0);       
    deselect();    
    int val = lower_byte|(upper_byte << 8);
    return val;
}

void mcp23s18::set_all_inverted() {
    set_inverted(IOX_ALLINVERTED);
}

void mcp23s18::set_none_inverted() {
    set_inverted(IOX_NONEINVERTED);
}    

void mcp23s18::set_pullups(unsigned int pupins) {
    select();
    spi.write(MCP23S18WRADDR);
    spi.write(GPPUA_BANK0);
    spi.write(0x000000FF & pupins);    
    spi.write(0x000000FF & (pupins>>8));
    deselect();    
}

int mcp23s18::read_pullups() {
    select();
    spi.write(MCP23S18RDADDR);
    spi.write(GPPUA_BANK0);   
    int lower_byte = spi.write(GPPUB_BANK0);
    int upper_byte = spi.write(GPPUA_BANK0);       
    deselect();    
    int val = lower_byte|(upper_byte << 8);
    return val;
}

void mcp23s18::set_all_pullups() {
    set_pullups(0xFFFF);    
}

void mcp23s18::set_none_pullups() {
    set_pullups(0x0000);    
}


void mcp23s18::write_port(unsigned int value) {
    //printf("Select MUX A\r\n");
    select();
    spi.write(MCP23S18WRADDR);
    spi.write(OLATA_BANK0);
    spi.write(0x000000FF & value);
    deselect();
    //printf("Deselect MUX A\r\n");
    //printf("Select MUX B\r\n");
    select();
    spi.write(MCP23S18WRADDR);
    spi.write(OLATB_BANK0);
    spi.write(0x000000FF & (value>>8));
    deselect();
    //printf("Deselect MUX B\r\n");
}
