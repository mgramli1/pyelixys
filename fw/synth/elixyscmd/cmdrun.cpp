#include "cmdrun.h"

//Debug is disabled by default
#if 0
#define DBG(x, ...) std::printf("[CMDRUN : DBG]"x"\r\n", ##__VA_ARGS__); 
#define WARN(x, ...) std::printf("[CMDRUN : WARN]"x"\r\n", ##__VA_ARGS__); 
#define ERR(x, ...) std::printf("[CMDRUN : ERR]"x"\r\n", ##__VA_ARGS__); 
#else
#define DBG(x, ...) 
#define WARN(x, ...)
#define ERR(x, ...) 
#endif

#define INFO(x, ...) printf("[CMDRUN : INFO]"x"\r\n", ##__VA_ARGS__);

void run_cmd(CMDPKT *pkt) {
    DBG("Executing pkt %d", pkt->cmd_id);
    switch(pkt->cmd_id) {
        case MIXERSSETDUTYCYCLE:
            mixer_set_duty_cycle(pkt);
            break;
        case MIXERSSETPERIOD:
            mixer_set_period(pkt);
            break;
        case VALVESSETSTATE0:
            valves_set_state0(pkt);
            break;
        case VALVESSETSTATE1:
            valves_set_state1(pkt);
            break;
        case VALVESSETSTATE2:
            valves_set_state2(pkt);
            break;
        case TEMPCTRLSETSETPOINT:
            tempctrl_set_setpoint(pkt);
            break;
        case TEMPCTRLTURNON:
            tempctrl_turn_on(pkt);
            break;
        case TEMPCTRLTURNOFF:
            tempctrl_turn_off(pkt);
            break;
        case SMCINTFSETANALOGOUT:
            smcintf_set_analog_out(pkt);
            break;
        case FANSTURNON:
            fan_turn_on(pkt);
            break;
        case FANSTURNOFF:
            fan_turn_off(pkt);
            break;
        case LINACTSETREQUESTEDPOSITION:
            linacts_set_req_pos(pkt);
            break;
        case LINACTHOMEAXIS:
            linacts_home_axis(pkt);
            break;
        case LINACTGATEWAYSTART:
            linacts_gateway_start(pkt);
            break;
        case LINACTTURNON:
            linacts_turn_on(pkt);
            break;
        case LINACTPAUSE:
            linacts_pause(pkt);
            break;
        case LINACTBRAKERELEASE:
            linacts_break_release(pkt);
            break;
        case LINACTRESET:
            linacts_reset(pkt);
            break;
        case LINACTSTART:
            linacts_start(pkt);
        default:
            ERR("Invalid cmd_id=%d", pkt->cmd_id);
            break;
    }
    
}