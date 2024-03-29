#ifndef CMDMSG_H_
#define CMDMSG_H_

// Template Author: Henry Herman
// Author email: hherman@mednet.ucla.edu


// This is an autogenerated file.
// It was created by pyelixys.hal.cmdfmt.py
// To ensure proper communication do not modify this file
// UNLESS you really know what you are doing!

#define SMCINTFSETANALOGOUT  (9)
#define TEMPCTRLSETSETPOINT  (6)
#define TEMPCTRLTURNON  (7)
#define TEMPCTRLTURNOFF  (8)
#define FANSTURNON  (10)
#define FANSTURNOFF  (11)
#define MIXERSSETPERIOD  (1)
#define MIXERSSETDUTYCYCLE  (2)
#define LINACTSETREQUESTEDPOSITION  (12)
#define LINACTHOMEAXIS  (13)
#define LINACTGATEWAYSTART  (14)
#define LINACTTURNON  (15)
#define LINACTPAUSE  (16)
#define LINACTSTART  (17)
#define LINACTBRAKERELEASE  (18)
#define LINACTRESET  (19)
#define VALVESSETSTATE0  (3)
#define VALVESSETSTATE1  (4)
#define VALVESSETSTATE2  (5)
#define MAXPARAMLEN  512




typedef struct __attribute__ ((__packed__)){
    int cmd_id;
    int device_id;
    char parameter[MAXPARAMLEN];
} CMDPKT;

extern CMDPKT cmd_pkt;

#endif // End cmdmsg guard