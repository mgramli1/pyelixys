#include "elixys.h"


using namespace IAI;

namespace Elixys {

    // Linear Actuator Com Port
    LinearActuatorCom actuator(P0_15, P0_16, P0_17);

    // SPI Communication Bus
    SPI spibus(P0_9,P0_8,P0_7);
    
    // Fan Subsystem
    PwmOut fan1(P2_4);
    PwmOut fan2(P2_5);
    DigitalOut fan0(P2_8);
    DigitalOut misc0(P0_19);
    
    using namespace IAI;
    
    // Heater Subsystem
    unsigned int heater_state;
    mcp23s18 htriomux(spibus, selectheater, unselect);
    
    void setup_heater() {
            htriomux.initialize();    
            htriomux.set_all_output();
            heater_state = ALLHEATERSOFF;
            turn_off_heater(ALLHEATERSOFF);
    }
    
    void turn_on_heater(unsigned int pins) {
            heater_state &= ~(pins);
            htriomux.write_port(heater_state);
    }
    
    void turn_off_heater(unsigned int pins) {
            heater_state |= (pins);
            htriomux.write_port(heater_state);
    }
    
    void set_heater_state(unsigned int pins) {
        htriomux.write_port(~pins);
    }
    
    // Mixer Subsystem    
    PwmOut mtr0(P2_0);
    PwmOut mtr1(P2_1);
    PwmOut mtr2(P2_2);
    PwmOut mtr3(P2_3);
    
    // SMCInteface Subsystem
    MCP3202 smcadc(spibus, selectsmcadc, unselect);
    MCP482X smcdac(spibus, selectsmcdac, unselect);

    // Thermocouple Interface
    max31855 tcintf0(spibus, selecttc0, unselect);
    max31855 tcintf1(spibus, selecttc1, unselect);
    max31855 tcintf2(spibus, selecttc2, unselect);
    max31855 tcintf3(spibus, selecttc3, unselect);
    max31855 tcintf4(spibus, selecttc4, unselect);
    max31855 tcintf5(spibus, selecttc5, unselect);
    max31855 tcintf6(spibus, selecttc6, unselect);
    max31855 tcintf7(spibus, selecttc7, unselect);
    max31855 tcintf8(spibus, selecttc8, unselect);
    
    
    // Valve Subsystem
    DigitalOut valvrst(P2_7);

    mcp23s18 val0iomux(spibus, selectvalve0, unselect);    
    mcp23s18 val1iomux(spibus, selectvalve1, unselect); 
    mcp23s18 val2iomux(spibus, selectvalve2, unselect); 
    
    void setup_valves() {
        valvrst = 0;
        valvrst = 1;
        val0iomux.initialize();
        val1iomux.initialize();
        val2iomux.initialize();
        
        val0iomux.set_all_output();
        val1iomux.set_all_output();
        val2iomux.set_all_output();
        
        val0iomux.write_port(0);
        val1iomux.write_port(0);
        val2iomux.write_port(0);
    }
    
    void set_valves(int id, int value) {
        if(id == 0) {
            val0iomux.write_port(value);
        } else if(id == 1) {
            val1iomux.write_port(value);
        } else if(id == 2) {
            val2iomux.write_port(value);
        }
    }
    
    
    // Position Sensors Subsystem
    mcp23s18 posiomux(spibus, selectpos, unselect);     
    DigitalOut posrst(P2_12);
    
    void setup_position_sensors() {
        posrst = 0;
        posrst = 1;
        posiomux.initialize();
        posiomux.set_none_pullups();
        posiomux.set_all_input();         
    }
    
    // SMC DAC Setup
    void setup_smc_interface() {
        smcdac.setGainA(2);
        smcdac.setGainB(2);        
    }
    
    // Liquid Sensor Subsystem    
    mcp3208 liqadc(spibus, selectliq, unselect);

    void setup_elixys() {
        setup_heater();
        setup_valves();
        setup_position_sensors();
        setup_smc_interface();
    }
    
#ifdef SYSTEMTEST    
    // System Tests

    void fan_test() {            
        
        fan1 = 1.0;
        fan2 = 1.0;
        fan0 = 1;
        misc0 = 1;
        
        for(int i=0;i<5;i++) {
            printf("FANTEST:%d\r\n", i);
            for(float val=0.05;val<1.0;val=val+0.1) {         
                printf("FANVALUE:%f\r\n",val);
                fan1 = val;
                fan2 = val;
                fan0 = !fan0;
                misc0 = !misc0;
                wait(0.05);                
            }            
        }
        fan0 = 0;
        misc0 = 0;
        fan1 = 0.0;
        fan2 = 0.0;        
    }
    
    void heater_test() {
         setup_heater();       
         printf("HEATERTEST\r\n");
         turn_on_heater(HEATER0);         
         wait(0.1);
         turn_off_heater(HEATER0);
         turn_on_heater(HEATER1);
         wait(0.1);
         turn_off_heater(HEATER1);
         turn_on_heater(HEATER2);
         wait(0.1);
         turn_off_heater(HEATER2);
         turn_on_heater(HEATER3);
         wait(0.1);
         turn_off_heater(HEATER3);
         turn_on_heater(HEATER4);
         wait(0.1);
         turn_off_heater(HEATER4);
         turn_on_heater(HEATER5);
         wait(0.1);
         turn_off_heater(HEATER5);
         turn_on_heater(HEATER6);
         wait(0.1);
         turn_off_heater(HEATER6);
         turn_on_heater(HEATER7);
         wait(0.1);
         turn_off_heater(HEATER7);
         turn_on_heater(HEATER8);
         wait(0.1);
         turn_off_heater(HEATER8);
         turn_on_heater(HTRLED0);
         wait(0.1);     
         turn_off_heater(HTRLED0);
         turn_on_heater(HTRLED1);
         wait(0.1);
         turn_off_heater(HTRLED2);
         turn_on_heater(VAC);
         wait(0.1);
         turn_off_heater(VAC);                   
    }
    
    void mixer_test() { 
        mtr0 = 1.0;
        mtr1 = 1.0;
        mtr2 = 1.0;
        mtr3 = 1.0;
        
        for(int i=0;i<5;i++) {
            printf("MIXERSTEST:%d\r\n", i);
            for(float val=0.1;val<1.1;val=val+0.1) {
                printf("MIXERVALUE:%f\r\n", val);
                wait(0.05);    
                mtr0 = val;
                mtr1 = val;
                mtr2 = val;
                mtr3 = val;                
            }
        }
        
        mtr0 = 0.0;
        mtr1 = 0.0;
        mtr2 = 0.0;
        mtr3 = 0.0;        
    }
    
    void smcadc_test() {
        printf("SMCADCs|ADC0:0x%x,ADC1:0x%x\r\n", smcadc.readA(), smcadc.readB());
    }
    
    void smcdac_test() {
        int ret;
        smcdac.setGainA(2);
        smcdac.setGainB(2); 
        for(int i = 0; i < 1024; i=i+16) {
            ret = smcdac.writeA(i);
            ret = smcdac.writeB(i);
            wait(0.01);
            printf("SMCDAC%d|ret%d\r\n", i, ret); 
        } 
    }
    
    int tc_test() {
        float fvalue[9];
        char resbuf[100]="\0";
        char valbuf[6] = "\0";
        fvalue[0] = tcintf0.read_temp();
        fvalue[1] = tcintf1.read_temp();
        fvalue[2] = tcintf2.read_temp();
        fvalue[3] = tcintf3.read_temp();
        fvalue[4] = tcintf4.read_temp();
        fvalue[5] = tcintf5.read_temp();
        fvalue[6] = tcintf6.read_temp();
        fvalue[7] = tcintf7.read_temp();
        fvalue[8] = tcintf8.read_temp();
        
        strcat(resbuf,"THERMOS");        
        for(int idx=0;idx<9;idx++) {        
            if (fvalue[idx] > 2000){
                if(fvalue[idx]==2001){
                    strcat(resbuf,"NoTC,");
                }else if(fvalue[idx]==2002){
                    strcat(resbuf,"ShrtGnd,");
                }else if(fvalue[idx]==2004){
                    strcat(resbuf,"ShrtVCC,");
                }
            }else{
                valbuf[0] = '\0';
                sprintf(valbuf,"%3.2f,", fvalue[idx]);
                strcat(resbuf,valbuf);                
            }
         }
         strcat(resbuf,"\r\n");         
         printf(resbuf); 
         return 0;    
    }
    
    void valve_test() {
        setup_valves();        
        for(int i=0;i<16;i++) {
            printf("VALVES:ID=%d\r\n",i);
            set_valves(0,(1<<i));
            set_valves(1,(1<<i));
            set_valves(2,(1<<i));
            wait(0.1);
        }  
        
        set_valves(0,0xFFFF);
        set_valves(1,0xFFFF);
        set_valves(2,0xFFFF);
        printf("VALVES:AllOn\r\n");
        wait(0.1); 
        set_valves(0,0x0000);
        set_valves(1,0x0000);
        set_valves(2,0x0000);
        printf("VALVES:AllOff\r\n");
        wait(0.1); 
    } 
    
    void position_sensor_test() {
        printf("POSITIONSTATE:0x%x\r\n", posiomux.read_port());
    }
    
    void liquid_sensors_test() {                
        printf("LIQUIDSENSORS|ADC0:0x%x,ADC1:0x%x,ADC2:0x%x,"
               "ADC3:0x%x,ADC4:0x%x,ADC5:0x%x,"
               "ADC6:0x%x,ADC7:0x%x\r\n",
                liqadc.read0(),
                liqadc.read1(),
                liqadc.read2(),
                liqadc.read3(),
                liqadc.read4(),
                liqadc.read5(),
                liqadc.read6(),
                liqadc.read7());    
    }
    
    void run_test() {
         valve_test(); 
         tc_test(); 
         heater_test();
         mixer_test();
         fan_test();
         smcadc_test();
         smcdac_test();  
         position_sensor_test();
         liquid_sensors_test();   
    }    
#endif    

// Elixys State update threads


}
