#ifndef MCP23S18_h
#define MCP23S18_h

#include "mbed.h"

// If you set IOCON.BANK = 0 then all
// the registers are 
// BUT each bank uses the lowest significant bit
// in the upper word for identifying the bank
// We will NOT use this method to address
// the registers since it hurts my head :)
// I am documenting these registers here simply
// as an exercise
#define MCP23S18WRADDR      0x40
#define MCP23S18RDADDR      0x41

#define IODIRA_BANK1        0x00
#define IODIRB_BANK1        0x10
#define IPOLA_BANK1         0x01
#define IPOLB_BANK1         0x11
#define GPINTENA_BANK1      0x02
#define GPINTENB_BANK1      0x12
#define DEFVALA_BANK1       0x03
#define DEFVALB_BANK1       0x13
#define INTCONA_BANK1       0x04
#define INTCONB_BANK1       0x14
#define IOCONA_BANK1        0x05
#define IOCONB_BANK1        0x15
#define GPPUA_BANK1         0x06
#define GPPUB_BANK1         0x16
#define INTFA_BANK1         0x07
#define INTFB_BANK1         0x17
#define INTCAPA_BANK1       0x08
#define INTCAPB_BANK1       0x18
#define GPIOA_BANK1         0x09
#define GPIOB_BANK1         0x19
#define OLATA_BANK1         0x0A
#define OLATB_BANK1         0x1A

// If you set IOCON.BANK = 1 then all
// the registers are set sequentially
// We will use this method to address
// the registers since it hurts my head less :)

#define IODIRA_BANK0        0x00
#define IODIRB_BANK0        0x01
#define IPOLA_BANK0         0x02
#define IPOLB_BANK0         0x03
#define GPINTENA_BANK0      0x04
#define GPINTENB_BANK0      0x05
#define DEFVALA_BANK0       0x06
#define DEFVALB_BANK0       0x07
#define INTCONA_BANK0       0x08
#define INTCONB_BANK0       0x09
#define IOCONA_BANK0        0x0A
#define IOCONB_BANK0        0x0B
#define GPPUA_BANK0         0x0C
#define GPPUB_BANK0         0x0D
#define INTFA_BANK0         0x0E
#define INTFB_BANK0         0x0F
#define INTCAPA_BANK0       0x10
#define INTCAPB_BANK0       0x11
#define GPIOA_BANK0         0x12
#define GPIOB_BANK0         0x13
#define OLATA_BANK0         0x14
#define OLATB_BANK0         0x15

#define IODIRn_IO0          (1<<0)
#define IODIRn_IO1          (1<<1)
#define IODIRn_IO2          (1<<2)
#define IODIRn_IO3          (1<<3)
#define IODIRn_IO4          (1<<4)
#define IODIRn_IO5          (1<<5)
#define IODIRn_IO6          (1<<6)
#define IODIRn_IO7          (1<<7)

#define IPOLn_IP0           (1<<0)
#define IPOLn_IP1           (1<<1)
#define IPOLn_IP2           (1<<2)
#define IPOLn_IP3           (1<<3)
#define IPOLn_IP4           (1<<4)
#define IPOLn_IP5           (1<<5)
#define IPOLn_IP6           (1<<6)
#define IPOLn_IP7           (1<<7)

#define GPINTENn_GPINT0     (1<<0)
#define GPINTENn_GPINT1     (1<<1)
#define GPINTENn_GPINT2     (1<<2)
#define GPINTENn_GPINT3     (1<<3)
#define GPINTENn_GPINT4     (1<<4)
#define GPINTENn_GPINT5     (1<<5)
#define GPINTENn_GPINT6     (1<<6)
#define GPINTENn_GPINT7     (1<<7)

#define DEFVALn_DEF0        (1<<0)
#define DEFVALn_DEF1        (1<<1)
#define DEFVALn_DEF2        (1<<2)
#define DEFVALn_DEF3        (1<<3)
#define DEFVALn_DEF4        (1<<4)
#define DEFVALn_DEF5        (1<<5)
#define DEFVALn_DEF6        (1<<6)
#define DEFVALn_DEF7        (1<<7)

#define INTCONn_IOC0        (1<<0)
#define INTCONn_IOC1        (1<<1)
#define INTCONn_IOC2        (1<<2)
#define INTCONn_IOC3        (1<<3)
#define INTCONn_IOC4        (1<<4)
#define INTCONn_IOC5        (1<<5)
#define INTCONn_IOC6        (1<<6)
#define INTCONn_IOC7        (1<<7)

#define IOCON_INTCC         (1<<0)
#define IOCON_INTPOL        (1<<1)
#define IOCON_ODR           (1<<2)
#define IOCON_RSVD0         (1<<3)
#define IOCON_RSVD1         (1<<4)
#define IOCON_SEQOP         (1<<5)
#define IOCON_MIRROR        (1<<6)
#define IOCON_BANK          (1<<7)
#define IOX_ALLOUTPUT       0x00000000
#define IOX_ALLINPUT        0xFFFFFFFF 
#define IOX_ALLINVERTED     0x00000000
#define IOX_NONEINVERTED    0xFFFFFFFF

class mcp23s18
{
    SPI& spi;
    void(*selectfxn)(void);
    void(*unselectfxn)(void);
    //DigitalOut ncs;    
  public:
  
    mcp23s18(SPI& _spi, void(*sel)(void), void(*usel)(void));
    void configspi();
    void select();
    void deselect();
    int initialize(int setType=0);    
    int read_config();
    void set_direction(unsigned int dirpins);
    int read_direction();
    void set_all_output();
    void set_all_input();
    
    void set_inverted(unsigned int dirpins);
    void set_all_inverted();
    void set_none_inverted();
    
    void set_pullups(unsigned int pupins);
    int read_pullups();
    void set_all_pullups();
    void set_none_pullups();
    
    void write_port(unsigned int value);

    int read_register(char reg);
    
    int read_port();
    int read_latch();
        
    int faultCode;
    
  private:
    float _error;
};

#endif
