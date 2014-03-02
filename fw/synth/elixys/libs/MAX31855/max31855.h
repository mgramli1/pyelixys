#ifndef MAX31855_h
#define MAX31855_h

#include "mbed.h"

class max31855
{
    SPI& spi;
    void(*selectfxn)(void);
    void(*unselectfxn)(void);
    //DigitalOut ncs;
    Timer pollTimer;
  public:
  
    max31855(SPI& _spi, void(*sel)(void), void(*usel)(void));
    void select();
    void deselect();
    void initialise(int setType=0);
        
    int faultCode;
    
    float chipTemp;
    float read_temp();
  private:
    PinName _CS_pin;
    PinName _SO_pin;
    PinName _SCK_pin;
    int _units;
    float _error;
};

#endif
