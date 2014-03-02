
#include "mbed.h"
#include "RPCVariable.h"
#include "RPCFunction.h"
#include "mbed_rpc.h"
#include "USBSerial.h"
#include "MCP482X.h"
#include "ShiftRegister.h"

int dacval0 = 0x00;  // DAC0 setpt
int dacval1 = 0x00;  // DAC1 setpt

// RPC Buffers
char buf[RPC_MAX_STRING], outbuf[RPC_MAX_STRING];

// Peripheral Setup
void serialCallback();
void setupLedPin();

// Utility Functions
void updateDAC();


// RPC Command Setup
RPC cboxrpc("cbox");

void toggleLed(Arguments*, Reply*);
void setLEDs(Arguments *args, Reply *reply);
void getADC(Arguments *args, Reply *reply);
void setDAC(Arguments *args, Reply *reply);
void pwrDAC(Arguments *args, Reply *reply);
void ssrelay(Arguments *args, Reply *reply);

RPCFunction BlinkyRPC(&toggleLed, "BLINK");
RPCFunction SetLEDsRPC(&setLEDs, "LEDS");
RPCFunction getADCRPC(&getADC, "ADC");
RPCFunction setDACRPC(&setDAC, "DAC");
RPCFunction setDACPWRRPC(&pwrDAC, "DACEN");
RPCFunction RelayRPC(&ssrelay, "SSR");

// Peripheral Setup

DigitalOut statled0(LED1);
DigitalOut statled1(LED2);
DigitalOut relay0(P1_2);
DigitalOut relay1(P1_3);
DigitalOut ledclk(P0_17);
DigitalOut leddat(P0_21);
DigitalOut ledlatch(P0_20);
DigitalOut ledclr(P1_4);
DigitalOut ledoe(P1_5);
AnalogIn ain0(P0_11);
AnalogIn ain1(P0_12);
SPI spi(P0_9,P0_8,P0_10);
DigitalOut daccs0(P1_0);
DigitalOut daccs1(P1_1);
USBSerial serial;

MCP482X dac0(spi, daccs0);
MCP482X dac1(spi, daccs1);

ShiftRegister shiftreg(ledclk, leddat, ledlatch, ledclr, ledoe);

int main() {
    setupLedPin(); 
    dac0.setGainA(2);
    dac1.setGainA(2);
    serial.attach(serialCallback);    
    setupLedPin(); 
    statled0 = 0;
    relay0=0;
    relay1=0;    
    while(1) {
        // Do nothing and wait for commands
    };
}

void serialCallback() {
    if(serial.available()) {
        serial.gets(buf, RPC_MAX_STRING);    
        cboxrpc.call(buf, outbuf);
        serial.printf("%s\n", outbuf);
    }
}

void setupDACs() {
    dac0.setGainA(2);
    dac1.setGainA(2);
}


void setupLedPin() {
    ledclk = 1;
    leddat = 1;
    ledclr = 0;
    ledoe = 1;     
    ledclr = 1;
    ledoe = 0;      
}

void setLEDs(Arguments *args, Reply *reply){
    char resp[16];
    if (args->argc != 1) {
        reply->putData("ERRARGNO");
        return;
    }
        
    int val = 0xFFFFFF;    
    sscanf(args->argv[0], "%x", &val);
    sprintf(resp, "LEDS %X", val);
    reply->putData(resp);
    shiftreg.write(val,24);
     
}


void toggleLed(Arguments *args, Reply *reply) {
    statled1 = !statled1;
    reply->putData(";)");        
}

void getADC(Arguments *args, Reply *reply) {
    int adcselect = 0;
    int val, val0, val1;
    char resp[16];
    
    if (args->argc != 1) {
        val0 = ain0.read_u16();;
        val1 = ain1.read_u16();;
        sprintf(resp, "ADC %X, %X", val0, val1);
        reply->putData(resp);
        return;
    }   
        
    sscanf(args->argv[0], "%d", &adcselect);
    if (adcselect == 0) {
        val = ain0.read_u16();
    } else if (adcselect == 1) {
        val = ain1.read_u16();
    } else {
        reply->putData("ERRADCNO");
        return;
    }    
    sprintf(resp, "ADC %d %d", adcselect, val);
    reply->putData(resp);
}

void setDAC(Arguments *args, Reply *reply) {
    int dacselect = 0;
    int val = 0;
    char resp[16];
    int ret;

     if (args->argc != 2) {
        sprintf(resp, "DAC %X, %X", dacval0, dacval1);
        reply->putData(resp);
        return;
    }   

    
    sscanf(args->argv[0], "%d", &dacselect);
    sscanf(args->argv[1], "%x", &val);
    
    if (dacselect == 0) {
        // Set DAC0
        ret = dac0.writeA(val);
        dacval0 = val;
    } else if (dacselect == 1) {
        // Set DAC1
        ret = dac1.writeA(val);
        dacval1 = val;
    } else {
        reply->putData("ERRDACNO");
        return;
    }    
    sprintf(resp, "DAC %d %x", dacselect, ret);
    reply->putData(resp); 
}

void pwrDAC(Arguments *args, Reply *reply) {
    int dacselect = 0;
    int val = 0;
    char resp[16];

    if (args->argc != 2) {
        reply->putData("ERRARGNO");
        return;
    }    
    
    sscanf(args->argv[0], "%d", &dacselect);
    sscanf(args->argv[1], "%x", &val);
    
    if ((dacselect != 0)&&(dacselect != 1)) {
        reply->putData("ERRDACNO");
        return;
    }
    
    if ((val != 0)&&(val != 1)) {
        reply->putData("ERRDACVAL");
        return;
    }
    
    if(dacselect==0 && val==1)
        dac0.enable();
    else
        dac0.disable();
    
    if(dacselect==1 && val==1)
        dac1.enable();
    else
        dac1.disable();
    
    sprintf(resp, "DACPWR %d %x", dacselect, val);
    reply->putData(resp); 
}

void ssrelay(Arguments *args, Reply *reply) {
    int relayselect = 0;
    int val = 0;
    char resp[16];
    
    if (args->argc != 2) {
        // Return the current SSR states
        sprintf(resp, "SSR %d, %d", relay0.read(), relay1.read());
        reply->putData(resp);
        return;
    }    
      
    
    sscanf(args->argv[0], "%d", &relayselect);
    sscanf(args->argv[1], "%x", &val);
    
    if ((relayselect != 0)&&(relayselect != 1)) {
        reply->putData("ERRSSRNO");
        return;
    }
    
    if ((val != 0)&&(val != 1)) {
        reply->putData("ERRSSRVAL");
        return;
    }
    
    if(relayselect==0) {
    if(val==1)
        relay0.write(1);
    else
        relay0.write(0);
    }
    
    if(relayselect==1) {
    if(val==1)
        relay1.write(1);
    else
        relay1.write(0);
    }
    
    sprintf(resp, "SSR %d %x", relayselect, val);
    reply->putData(resp); 
}
