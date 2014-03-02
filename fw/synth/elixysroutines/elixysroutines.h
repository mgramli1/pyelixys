#ifndef ELIXYSTHREADS_H
#define ELIXYSTHREADS_H
#include "mbed.h"
#include "elixys.h"
#include "statusmsg.h"
#include "cmdcallbacks.h"

#define TEMPCTRLRUNAWAY     2
#define TEMPCTRLGOOD        0


namespace Elixys {
    void thermocouple_routine();
    void liquid_sensor_routine();
    void postion_sensor_routine();
    void smcinterface_adc_routine();
    void temperature_controller_routine();
    void linear_actuator_routine();
    void elixys_routines();
}
#endif // ELIXYSTHREADS_H
