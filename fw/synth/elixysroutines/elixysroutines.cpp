#include "elixysroutines.h"

namespace Elixys {
    
    // Helper function sets the thermocouple error code
    void set_thermocouple_error(int id) {        
        if(status.thermocouples.thermocouple[id].temperature == 2001) {
            status.thermocouples.thermocouple[id].error_code = TC_UNCONNECTED; 
        } else if(status.thermocouples.thermocouple[id].temperature == 2002) {
            status.thermocouples.thermocouple[id].error_code = TC_SHRTLO; 
        } else if(status.thermocouples.thermocouple[id].temperature == 2004) {
            status.thermocouples.thermocouple[id].error_code = TC_SHRTHI;             
        } else {
            status.thermocouples.thermocouple[id].error_code = TC_GOOD;
        }
    }    

    // Load the thermocouple values in to the states packet
    void thermocouple_routine() {
        status_mutex.lock();            
        status.thermocouples.thermocouple[0].temperature =  tcintf0.read_temp();                               
        status.thermocouples.thermocouple[1].temperature =  tcintf1.read_temp();
        status.thermocouples.thermocouple[2].temperature =  tcintf2.read_temp();
        status.thermocouples.thermocouple[3].temperature =  tcintf3.read_temp();
        status.thermocouples.thermocouple[4].temperature =  tcintf4.read_temp();
        status.thermocouples.thermocouple[5].temperature =  tcintf5.read_temp();
        status.thermocouples.thermocouple[6].temperature =  tcintf6.read_temp();
        status.thermocouples.thermocouple[7].temperature =  tcintf7.read_temp();
        status.thermocouples.thermocouple[8].temperature =  tcintf8.read_temp();        
        for(int i=0;i<THERMOCOUPLESCOUNT;i++) {
            set_thermocouple_error(i);  
        }                                                     
        status_mutex.unlock();                    
    }
    
    void liquid_sensor_routine() {
        status_mutex.lock();
        status.liquidsensors.error_code = 0;
        status.liquidsensors.liquidsensor[0].analog_in = liqadc.read0();        
        status.liquidsensors.liquidsensor[1].analog_in = liqadc.read1();
        status.liquidsensors.liquidsensor[2].analog_in = liqadc.read2();
        status.liquidsensors.liquidsensor[3].analog_in = liqadc.read3();
        status.liquidsensors.liquidsensor[4].analog_in = liqadc.read4();
        status.liquidsensors.liquidsensor[5].analog_in = liqadc.read5();
        status.liquidsensors.liquidsensor[6].analog_in = liqadc.read6();
        status.liquidsensors.liquidsensor[7].analog_in = liqadc.read7();
        status_mutex.unlock();                
    
    }
    
    void postion_sensor_routine() {
        status_mutex.lock();
        status.digitalinputs.state = posiomux.read_port();
        status.digitalinputs.error_code = 0;
        status_mutex.unlock();
    }
    
    void smcinterface_adc_routine() {
        status_mutex.lock();
        status.smcinterfaces.smcinterface[0].analog_in = smcadc.readA();
        status.smcinterfaces.smcinterface[1].analog_in = smcadc.readB();
        status_mutex.unlock();
    }
    
    unsigned int set_temperature_controller_heater(int heaterid, unsigned int heater_state) {
        if(status.temperaturecontrollers.temperaturecontroller[heaterid].error_code & (1<<TEMPCTRLONBIT)) {
            // Turn heater on!            
            if ((status.temperaturecontrollers.temperaturecontroller[heaterid].setpoint > 
                        status.thermocouples.thermocouple[heaterid].temperature)&&
                        status.thermocouples.thermocouple[heaterid].temperature<=200.0){
                heater_state |= 1<<heaterid;
            } else {
                heater_state &= ~(1<<heaterid);
            }
        } else {
            // Turn heater off!            
            heater_state &= ~(1<<heaterid);
        }               
                                  
        return heater_state;               
    }
    
    unsigned int set_temperature_controller_heater_led(unsigned int heater_state) {
        if( (status.temperaturecontrollers.temperaturecontroller[0].error_code & (1<<TEMPCTRLONBIT)) || 
            (status.temperaturecontrollers.temperaturecontroller[1].error_code & (1<<TEMPCTRLONBIT)) ||
            (status.temperaturecontrollers.temperaturecontroller[2].error_code & (1<<TEMPCTRLONBIT)) ) {
            heater_state |= HTRLED0;
        }

        if( (status.temperaturecontrollers.temperaturecontroller[3].error_code & (1<<TEMPCTRLONBIT)) || 
            (status.temperaturecontrollers.temperaturecontroller[4].error_code & (1<<TEMPCTRLONBIT)) ||
            (status.temperaturecontrollers.temperaturecontroller[5].error_code & (1<<TEMPCTRLONBIT)) ) {
            heater_state |= HTRLED1;
        }
        
        if( (status.temperaturecontrollers.temperaturecontroller[6].error_code & (1<<TEMPCTRLONBIT)) || 
            (status.temperaturecontrollers.temperaturecontroller[7].error_code & (1<<TEMPCTRLONBIT)) ||
            (status.temperaturecontrollers.temperaturecontroller[8].error_code & (1<<TEMPCTRLONBIT)) ) {
            heater_state |= HTRLED2;
        }        

        return heater_state;
    }
    
    unsigned int temperature_controller_safety_check(unsigned int heater_state) {
        for(int htrid=0;htrid<TEMPERATURECONTROLLERSCOUNT;htrid++) {
            if(status.thermocouples.thermocouple[htrid].temperature>=200.0) {
                status.temperaturecontrollers.error_code = TEMPCTRLRUNAWAY;
                return 0;                
            }             
        }
        status.temperaturecontrollers.error_code = TEMPCTRLGOOD;
        return heater_state;
    }
    
    
    void temperature_controller_routine() {
        unsigned int heater_state = 0;            
        for(int i=0; i<TEMPERATURECONTROLLERSCOUNT;i++) {            
            heater_state = set_temperature_controller_heater(i,heater_state);   
        }
        heater_state = set_temperature_controller_heater_led(heater_state);        
        //printf("Heater state %x\r\n", heater_state);                
        //heater_state = temperature_controller_safety_check(heater_state);
        set_heater_state(heater_state);                  
        status.heaters.state = (short)heater_state;
    }
    
    void linear_actuator_routines() {
          
        actuator.getGwStatusQuery();
        actuator.send();
        actuator.readResponse();
        status.linearactuators.error_code = actuator.getGwStatus();
        
        //for(int i=0;i<LINEARACTUATORSCOUNT;i++) {
        for(int i=0;i<1;i++) {
            actuator.getAxisStatusQuery(i);
            actuator.send();
            actuator.readResponse();
            status.linearactuators.linearactuator[i].error_code = actuator.getStatus();
            
            actuator.getAxisPosQuery(i);
            actuator.send();
            actuator.readResponse();
            status.linearactuators.linearactuator[i].position = actuator.getPosition();
        }
    }
    
    void elixys_routines() {
        thermocouple_routine();
        liquid_sensor_routine();
        postion_sensor_routine();
        smcinterface_adc_routine();   
        linear_actuator_routines();     
    }

    

} // end Elixys namespace