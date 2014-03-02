#include "mbed.h"
#include "elixys.h"
#include "rtos.h"
#include "EthernetInterface.h"
#include "Websocket.h"
#include "statusmsg.h"
#include "cmdmsg.h"
#include "cmdrun.h"
#include "elixysroutines.h"


#if 1
extern "C" void mbed_mac_address(char *mac) { mac[0] = 0x12; mac[1] = 0x34; mac[2] = 0x56; mac[3] = 0x78; mac[4] = 0x9a; mac[5] = 0xbc; } 
#endif

DigitalOut ethrst(P1_28);

DigitalOut statled1(LED1);
DigitalOut statled4(LED4);
Ticker stattick;
Ticker tempctrltick;
using namespace Elixys;   

void cb_statled() {
    statled1 = !statled1;
}


int main() {
    printf("Done setting up thermocouple thread\r\n");
    ethrst = 0;
    wait(0.01);
    ethrst = 1;
    EthernetInterface eth;
    setup_elixys();
    printf("Running Init\r\n");
    eth.init(); //Use DHCP
    printf("Getting DHCP\r\n");    
    eth.connect();
    printf("IP Address is %s\r\n", eth.getIPAddress());
    
    status.header.packet_id = 1;
    status.header.packet_type = '?';
    status.header.system_error_code = 0;
    status.digitalinputs.error_code = 'A';
    status.liquidsensors.error_code = 'B';
    status.fans.state = 0x01;
    status.thermocouples.thermocouple[7].error_code = 'C';
    status.thermocouples.thermocouple[7].temperature = 10.1;
    //status.liquidsensors.liquidsensor[0].analog_in = 5;
    
    printf("******************************\r\n");
    printf("ID\t\t\tSIZE\r\n");
    printf("HEADER\t\t\t %d bytes\r\n", sizeof(HEADER));
    printf("MIXERS\t\t\t %d bytes\r\n", sizeof(MIXERS));
    printf("VALVES\t\t\t %d bytes\r\n", sizeof(VALVES));
    printf("THERMOCOUPLES\t\t\t %d bytes\r\n", sizeof(THERMOCOUPLES));
    printf("AUXTHERMOCOUPLES\t\t\t %d bytes\r\n", sizeof(AUXTHERMOCOUPLES));
    printf("HEATERS\t\t\t %d bytes\r\n", sizeof(HEATERS));
    printf("TEMPERATURECONTROLLERS\t\t\t %d bytes\r\n", sizeof(TEMPERATURECONTROLLERS));
    printf("SMCINTERFACES\t\t\t %d bytes\r\n", sizeof(SMCINTERFACES));
    printf("FANS\t\t\t %d bytes\r\n", sizeof(FANS));
    printf("LINEARAXIS\t\t\t %d bytes\r\n", sizeof(LINEARACTUATOR));
    printf("DIGITALINPUTS\t\t\t %d bytes\r\n", sizeof(DIGITALINPUTS));
    printf("LIQUIDSENSORS\t\t\t %d bytes\r\n", sizeof(LIQUIDSENSORS));
    printf("******************************\r\n");
    int total_bytes;
    total_bytes = sizeof(HEADER)
                  + sizeof(MIXERS)
                  + sizeof(VALVES)
                  + sizeof(THERMOCOUPLES)
                  + sizeof(AUXTHERMOCOUPLES)
                  + sizeof(HEATERS)
                  + sizeof(TEMPERATURECONTROLLERS)
                  + sizeof(SMCINTERFACES)
                  + sizeof(FANS)
                  + sizeof(LINEARACTUATORS)
                  + sizeof(DIGITALINPUTS)
                  + sizeof(LIQUIDSENSORS);
    printf("Total packet size should be %d =/= %d\r\n", total_bytes, sizeof(STATUSPKT));
    
    
    
    stattick.attach(&cb_statled,0.5);
    tempctrltick.attach(&temperature_controller_routine,0.02); 
                  
    Websocket ws("ws://192.168.1.101:8888/ws");            
    int ret = -1;                   
    while(1) {        
        elixys_routines();
        while(ret < 0) {
            elixys_routines();
            printf("Connection disconnected ERRCODE:%d\r\n", ret);
            if(ws.is_connected()) {
                ws.close();
            }
            
            if(ws.connect()) {
                ret = 0;
                status.header.packet_id=0;
            }            
        }        
        if((ws.read((char *)&cmd_pkt)) > 0) {
            //printf("**Rec CMD: %d\r\n", cmdlen);            
            printf("CMDID: %d\r\n", cmd_pkt.cmd_id);
            run_cmd(&cmd_pkt);
        }       
        status.header.packet_id++;
        ret = ws.send((void *)&status, sizeof(status));                        
                
    }    
    
}
