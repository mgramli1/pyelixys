#ifndef CMDCBS_H_
#define CMDCBS_H_
#include "cmdmsg.h"
#include "statusmsg.h"
#include "mbed.h"
#include "elixys.h"

#define TEMPCTRLONBIT 0
#define LINACTHOMEONBIT 0

// Mixer fxns
void mixer_set_period(CMDPKT *pkt);
void mixer_set_duty_cycle(CMDPKT *pkt);

// Fan fxns
void fan_turn_on(CMDPKT *pkt);
void fan_turn_off(CMDPKT *pkt);

// Temperature Controllers
void tempctrl_set_setpoint(CMDPKT *pkt);
void tempctrl_turn_on(CMDPKT *pkt);
void tempctrl_turn_off(CMDPKT *pkt);

// SMC Interface
void smcintf_set_analog_out(CMDPKT *pkt);

// Valves
void valves_set_state0(CMDPKT *pkt);
void valves_set_state1(CMDPKT *pkt);
void valves_set_state2(CMDPKT *pkt);

// Linear Actuators
void linacts_set_req_pos(CMDPKT *pkt);
void linacts_home_axis(CMDPKT *pkt);
void linacts_gateway_start(CMDPKT *pkt);
void linacts_turn_on(CMDPKT *pkt);
void linacts_pause(CMDPKT *pkt);
void linacts_break_release(CMDPKT *pkt);
void linacts_reset(CMDPKT *pkt);
void linacts_start(CMDPKT *pkt);


#endif // CMDCBS