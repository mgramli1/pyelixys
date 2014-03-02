#ifndef ELIXYS_H
#define ELIXYS_H
#include "mbed.h"
#include "chipselectarray.h"
#include "mcp23s18.h"
#include "mcp3202.h"
#include "mcp482x.h"
#include "max31855.h"
#include "mcp3208.h"
#include "linactcom.h"

#define SYSTEMTEST 1

// Fan Subsystem Defines

// Heater Subsystem Defines
#define HEATER0  (1<<0)
#define HEATER1  (1<<1)
#define HEATER2  (1<<2)
#define HEATER3  (1<<3)
#define HEATER4  (1<<4)
#define HEATER5  (1<<5)
#define HEATER6  (1<<6)
#define HEATER7  (1<<7)
#define HEATER8  (1<<8)
#define HTRLED0  (1<<9)
#define HTRLED1  (1<<10)
#define HTRLED2  (1<<11)
#define VAC  (1<<12)
#define ALLHEATERSOFF  0xFFFF
#define ALLHEATERSON  0x0000

// System Errors
// Thermocouples
#define TC_UNCONNECTED  0x02
#define TC_SHRTLO       0x04
#define TC_SHRTHI       0x08
#define TC_GOOD         0x00


using namespace IAI;

namespace Elixys {

    
    
    // SPI Communication Bus
    extern SPI spibus;

    extern LinearActuatorCom actuator;

    // Fan Subsystem
    extern PwmOut fan1;
    extern PwmOut fan2;
    extern DigitalOut fan0;
    extern DigitalOut misc0;
    
    // Linear Actuators
    //extern LinearActuatorCom linact;
    
    // Heater Subsystem
    extern mcp23s18 htriomux;
    
    void turn_on_heater(unsigned int pins);
    void turn_off_heater(unsigned int pins);
    void setup_heater();
    void set_heater_state(unsigned int pins);
   
    // Mixer Subsystem
    extern PwmOut mtr0;
    extern PwmOut mtr1;
    extern PwmOut mtr2;
    extern PwmOut mtr3;   
    
    
    // SMCInterface Subsystem
    extern MCP3202 smcadc;
    extern MCP482X smcdac;
    
    // Thermocouple Subsystem
    extern max31855 tcintf0;
    extern max31855 tcintf1;
    extern max31855 tcintf2;
    extern max31855 tcintf3;
    extern max31855 tcintf4;
    extern max31855 tcintf5;
    extern max31855 tcintf6;
    extern max31855 tcintf7;
    extern max31855 tcintf8; 

    void setup_valves();             
    void set_valves(int id, int value);    
    
    // Position Sensor Subsystem
    void setup_position_sensors();
    extern mcp23s18 posiomux;
    
    // Liquid Sensors Subsystem
    extern mcp3208 liqadc;
    
    // Elixys System Setup
    void setup_elixys();
    
    // System Tests
#ifdef SYSTEMTEST    
    void fan_test();
    void heater_test();
    void mixer_test();    
    void smcadc_test();
    void smcdac_test();
    int tc_test();
    void valve_test();
    void position_sensor_test();
    void run_test();
#endif

}
 

#endif //ELIXYS_H