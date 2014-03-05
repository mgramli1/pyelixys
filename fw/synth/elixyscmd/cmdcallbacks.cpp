#include "cmdcallbacks.h"
#include "rtos.h"

//Debug is disabled by default
#if 1
#define DBG(x, ...) std::printf("[CMDCBS : DBG]"x"\r\n", ##__VA_ARGS__); 
#define WARN(x, ...) std::printf("[CMDCBS : WARN]"x"\r\n", ##__VA_ARGS__); 
#define ERR(x, ...) std::printf("[CMDCBS : ERR]"x"\r\n", ##__VA_ARGS__); 
#else
#define DBG(x, ...) 
#define WARN(x, ...)
#define ERR(x, ...) 
#endif

#define INFO(x, ...) printf("[CMDCBS : INFO]"x"\r\n", ##__VA_ARGS__);

using namespace Elixys; 

// Mixer fxns
void mixer_set_period(CMDPKT *pkt) {
    DBG("Mixer.set_period");
    status_mutex.lock();
    status.mixers.mixer[pkt->device_id].period = *((float*)pkt->parameter);
    status_mutex.unlock();
}

void mixer_set_duty_cycle(CMDPKT *pkt) {    
    float val = 0;
    status_mutex.lock();        
    switch(pkt->device_id) {
        case 0:
            DBG("Mixer0.set_duty_cycle");
            status.mixers.mixer[pkt->device_id].duty_cycle = *((float*)pkt->parameter);
            val = status.mixers.mixer[pkt->device_id].duty_cycle / 100.0;
            if((val >=0.0) && (val <= 1.0)) { 
                mtr0 = val;
            } else {
                mtr0 = 0;
                // set error code, mixer invalid value
            }
            break;
        case 1:
            DBG("Mixer1.set_duty_cycle");
            status.mixers.mixer[pkt->device_id].duty_cycle = *((float*)pkt->parameter);
            val = status.mixers.mixer[pkt->device_id].duty_cycle / 100.0;
            if((val >=0.0) && (val <= 1.0)) { 
                mtr1 = val; 
            } else {
                mtr0 = 0;
                // set error code, mixer invalid value
            }
            break;
        case 2:
            DBG("Mixer2.set_duty_cycle");
            status.mixers.mixer[pkt->device_id].duty_cycle = *((float*)pkt->parameter);
            val = status.mixers.mixer[pkt->device_id].duty_cycle / 100.0;
            if((val >= 0.0) && (val <= 1.0)) { 
                mtr2 = val; 
            } else {
                mtr0 = 0;
                // set error code, mixer invalid value
            }                
            break;
        default:
                // set error code, invalid mixer device_id
            break;
    }
    status_mutex.unlock();
}

// Fan fxns
void fan_turn_on(CMDPKT *pkt) {
    DBG("Fan%d.turn_on", pkt->device_id);    
    status_mutex.lock();   
    status.fans.state |= (1 << pkt->device_id);
    status_mutex.unlock();   
    switch(pkt->device_id) {
        case 0:
            fan0 = 1;
            break;
        case 1:
            fan1 = 1.0;
            break;
        case 2:
            fan2 = 1.0;
            break;
        default:
            // Set fan id error
            break;
    }
}

void fan_turn_off(CMDPKT *pkt) {
    DBG("Fan%d.turn_off", pkt->device_id);    
    status_mutex.lock();   
    status.fans.state &= ~(1 << pkt->device_id);
    status_mutex.unlock();
    switch(pkt->device_id) {
        case 0:
            fan0 = 0;
            break;
        case 1:
            fan1 = 0.0;
            break;
        case 2:
            fan2 = 0.0;
            break;
        default:
            // Set fan id error
            break;
    }
}

// Temperature Controllers
void tempctrl_set_setpoint(CMDPKT *pkt) {
    DBG("TempCtrl.set_setpoint");
    status.temperaturecontrollers.
                temperaturecontroller[pkt->device_id].
                setpoint = *((float*)pkt->parameter);
}

void tempctrl_turn_on(CMDPKT *pkt) {
    DBG("TempCtrl.turn_on");
    status.temperaturecontrollers.
                temperaturecontroller[pkt->device_id].
                error_code |= 1<<TEMPCTRLONBIT;
       
}

void tempctrl_turn_off(CMDPKT *pkt) {
    DBG("TempCtrl.turn_off");
        status.temperaturecontrollers.
                temperaturecontroller[pkt->device_id].
                error_code &= ~(1<<TEMPCTRLONBIT); 
}

// SMC Interface
void smcintf_set_analog_out(CMDPKT *pkt) {
    
    status_mutex.lock(); 
    status.smcinterfaces.smcinterface[pkt->device_id].analog_out = *((float*)pkt->parameter);
    status_mutex.unlock(); 
    int dac_setpt = (status.smcinterfaces.smcinterface[pkt->device_id].analog_out/10.0*4095);
    DBG("SMCIntf%d.set_analog_out=%d",pkt->device_id, dac_setpt);
    switch(pkt->device_id) {
        case 0:
            smcdac.writeA(dac_setpt);
            break;
        case 1:
            smcdac.writeB(dac_setpt);
            break;
        default:
            // send device id error
            break;
    }    
}

// Valves
void valves_set_state0(CMDPKT *pkt){    
    status_mutex.lock(); 
    status.valves.state0 = *((short*)pkt->parameter);
    status_mutex.unlock();
    set_valves(0, status.valves.state0);
    DBG("Valves.set_state0=%x", status.valves.state0);
    
}

void valves_set_state1(CMDPKT *pkt){
    status_mutex.lock();
    status.valves.state1 = *((short*)pkt->parameter);
    status_mutex.unlock();
    set_valves(1, status.valves.state1);
    DBG("Valves.set_state1=%x", status.valves.state1);
}

void valves_set_state2(CMDPKT *pkt) {    
    status_mutex.lock();
    status.valves.state2 = *((short*)pkt->parameter);
    status_mutex.unlock();
    set_valves(2, status.valves.state2);
    DBG("Valves.set_state2=%x", status.valves.state2);
}

// Linear Actuators
void linacts_set_req_pos(CMDPKT *pkt) {
    int *posptr = (int*)pkt->parameter;
    int devid = pkt->device_id;
    
    DBG("LinActs.set_req_pos");  
    actuator.getSetAxisPosQuery(devid, *posptr);
    
    if (actuator.sendAndRead()!=0) {
        DBG("LinActs.set_req_pos:BADRESPERR");
        return;
    }
    status.linearactuators.
            linearactuator[pkt->device_id].
            requested_position = *posptr;
    DBG("LinActs.set_req_pos:OK");
}

void linacts_home_axis(CMDPKT *pkt) {
    int devid = pkt->device_id;
    DBG("LinActs.home_axis");
    
    actuator.getAxisHomeQuery(devid);
    
    if (actuator.sendAndRead()!=0) {
        DBG("LinActs.home_axis:BADRESPERR");
        return;
    }
    DBG("LinActs.home_axis:OK");
    
}

void linacts_gateway_start(CMDPKT *pkt) {
    DBG("LinActs.gateway_start");
    
    actuator.getGwStartQuery();
    
    if (actuator.sendAndRead()!=0) {
        DBG("LinActs.gateway_start:BADRESPERR");
        return;
    }
    DBG("LinActs.gateway_start:OK");   
    
}

void linacts_turn_on(CMDPKT *pkt) {
    int devid = pkt->device_id;
    DBG("LinActs.turn_on");
    
    actuator.getAxisOnQuery(devid);
    
    if (actuator.sendAndRead()!=0) {
        DBG("LinActs.turn_on:BADRESPERR");
        return;
    }
    DBG("LinActs.turn_on:OK");  
    
}

void linacts_pause(CMDPKT *pkt) {
    int devid = pkt->device_id;
    DBG("LinActs.pause");
    
    actuator.getAxisPauseQuery(devid);
    
    if (actuator.sendAndRead()!=0) {
        DBG("LinActs.pause:BADRESPERR");
        return;
    }
    DBG("LinActs.pause:OK");   
    
}

void linacts_break_release(CMDPKT *pkt) {
    int devid = pkt->device_id;
    DBG("LinActs.brake_release");
    
    actuator.getAxisBrakeReleaseQuery(devid);
    
    if (actuator.sendAndRead()!=0) {
        DBG("LinActs.brake_release:BADRESPERR");
        return;
    }
    DBG("LinActs.brake_release:OK");
    
}

void linacts_reset(CMDPKT *pkt) {
    DBG("LinActs.reset");
    int devid = pkt->device_id;
    
    actuator.getAxisResetQuery(devid);
    
    if (actuator.sendAndRead()!=0) {
        DBG("LinActs.reset:BADRESPERR");
        return;
    }
    DBG("LinActs.reset:OK");   
    
}

void linacts_start(CMDPKT *pkt) {
    DBG("LinActs.start");
    int devid = pkt->device_id;
    
    actuator.getAxisStartQuery(devid);
    
    if (actuator.sendAndRead()!=0) {
        DBG("LinActs.start:BADRESPERR");
        return;
    }
    DBG("LinActs.start:OK");  
      
}


// Threads
