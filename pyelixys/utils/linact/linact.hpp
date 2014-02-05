
#ifndef LINACT_H
#define LINACT_H

#define GWADDR       0x3f  // 63 or 0x3f fixed slave address
#define LINACT_READ_MULTI   0x03
#define LINACT_WRITE        0x06
#define LINACT_WRITE_MULTI  0x10

#define GWCTRL0      0xF600
#define GWCTRL1      0xF601

#define GWCTRL_APP_SIG      (1<<15)

#define AXIS0_BASE_WR        0xF608
#define AXIS1_BASE_WR        0xF60C
#define AXIS2_BASE_WR        0xF610
#define AXIS3_BASE_WR        0xF614
#define AXIS4_BASE_WR        0xF608
#define AXIS5_BASE_WR        0xF61C

#define POS_SET_LO_OFFSET    0x0

#define AXIS0_POS_SET_LO   (AXIS0_BASE_WR + POS_SET_LO_OFFSET)
#define AXIS1_POS_SET_LO   (AXIS1_BASE_WR + POS_SET_LO_OFFSET)
#define AXIS2_POS_SET_LO   (AXIS2_BASE_WR + POS_SET_LO_OFFSET)
#define AXIS3_POS_SET_LO   (AXIS3_BASE_WR + POS_SET_LO_OFFSET)
#define AXIS4_POS_SET_LO   (AXIS4_BASE_WR + POS_SET_LO_OFFSET)

#define POS_SET_HI_OFFSET   0x1

#define AXIS0_POS_SET_HI   (AXIS0_BASE_WR + POS_SET_HI_OFFSET)
#define AXIS1_POS_SET_HI   (AXIS1_BASE_WR + POS_SET_HI_OFFSET)
#define AXIS2_POS_SET_HI   (AXIS2_BASE_WR + POS_SET_HI_OFFSET)
#define AXIS3_POS_SET_HI   (AXIS3_BASE_WR + POS_SET_HI_OFFSET)
#define AXIS4_POS_SET_HI   (AXIS4_BASE_WR + POS_SET_HI_OFFSET)

#define CMD_POS_SET_NUM     0x2

#define AXIS0_CMD_POS_SET   (AXIS0_BASE_WR + CMD_POS_SET_NUM)
#define AXIS1_CMD_POS_SET   (AXIS1_BASE_WR + CMD_POS_SET_NUM)
#define AXIS2_CMD_POS_SET   (AXIS2_BASE_WR + CMD_POS_SET_NUM)
#define AXIS3_CMD_POS_SET   (AXIS3_BASE_WR + CMD_POS_SET_NUM)
#define AXIS4_CMD_POS_SET   (AXIS4_BASE_WR + CMD_POS_SET_NUM)

#define CNTRL_SIG

#define AXIS0_CTRL_SIG      (AXIS0_BASE_WR + CNTRL_SIG)
#define AXIS1_CTRL_SIG      (AXIS1_BASE_WR + CNTRL_SIG)
#define AXIS2_CTRL_SIG      (AXIS2_BASE_WR + CNTRL_SIG)
#define AXIS3_CTRL_SIG      (AXIS3_BASE_WR + CNTRL_SIG)
#define AXIS4_CTRL_SIG      (AXIS4_BASE_WR + CNTRL_SIG)

#define AXIS_CTRL_BKRL      (1<<15)
#define AXIS_CTRL_MODE      (1<<10)
#define AXIS_CTRL_PWRT      (1<<9)
#define AXIS_CTRL_JOGP      (1<<8)
#define AXIS_CTRL_JOGN      (1<<7)
#define AXIS_CTRL_JVEL      (1<<6)
#define AXIS_CTRL_JISL      (1<<5)
#define AXIS_CTRL_SON       (1<<4)
#define AXIS_CTRL_RES       (1<<3)
#define AXIS_CTRL_STP       (1<<2) // Pause command
#define AXIS_CTRL_HOME      (1<<1)
#define AXIS_CTRL_CSTR      (1<<0)

#define LINACT_GWSTATUS0    0xF700
#define LINACT_GWSTATUS1    0xF701

#define GWSTATUS0_RUN       (1<<15)
#define GWSTATUS0_ERRT      (1<<14)
#define GWSTATUS0_MOD       (1<<12)
#define GWSTATUS0_W8B16     (1<<9)
#define GWSTATUE0_W8B8      (1<<8)
#define GWSTATUS0_W8B4      (1<<7)
#define GWSTATUS0_W8B2      (1<<6)
#define GWSTATUS0_W8B1      (1<<5)
#define GWSTATUS0_W4B16     (1<<4)
#define GWSTATUS0_W4B8      (1<<3)
#define GWSTATUS0_W4B4      (1<<2)
#define GWSTATUS0_W4B2      (1<<1)
#define GWSTATUS0_W4B1      (1<<0)

#define GWSTATUS1_LNK15     (1<<15)
#define GWSTATUS1_LNK14     (1<<14)
#define GWSTATUS1_LNK13     (1<<13)
#define GWSTATUS1_LNK12     (1<<12)
#define GWSTATUS1_LNK11     (1<<11)
#define GWSTATUS1_LNK10     (1<<10)
#define GWSTATUS1_LNK9      (1<<9)
#define GWSTATUS1_LNK8      (1<<8)
#define GWSTATUS1_LNK7      (1<<7)
#define GWSTATUS1_LNK6      (1<<6)
#define GWSTATUS1_LNK5      (1<<5)
#define GWSTATUS1_LNK4      (1<<4)
#define GWSTATUS1_LNK3      (1<<3)
#define GWSTATUS1_LNK2      (1<<2)
#define GWSTATUS1_LNK1      (1<<1)
#define GWSTATUS1_LNK0      (1<<0)



#define AXIS0_BASE_RD       0xF708
#define AXIS1_BASE_RD       0xF70C
#define AXIS2_BASE_RD       0xF710
#define AXIS3_BASE_RD       0xF714
#define AXIS4_BASE_RD       0xF718


#define POS_GET_LO_OFFSET   0x0

#define AXIS0_POS_GET_LO    (AXIS0_BASE_RD + POS_GET_LO_OFFSET)
#define AXIS1_POS_GET_LO    (AXIS1_BASE_RD + POS_GET_LO_OFFSET)
#define AXIS2_POS_GET_LO    (AXIS2_BASE_RD + POS_GET_LO_OFFSET)
#define AXIS3_POS_GET_LO    (AXIS3_BASE_RD + POS_GET_LO_OFFSET)
#define AXIS4_POS_GET_LO    (AXIS4_BASE_RD + POS_GET_LO_OFFSET)

#define POS_GET_HI_OFFSET   0x1

#define AXIS0_POS_GET_HI    (AXIS0_BASE_RD + POS_GET_HI_OFFSET)
#define AXIS1_POS_GET_HI    (AXIS1_BASE_RD + POS_GET_HI_OFFSET)
#define AXIS2_POS_GET_HI    (AXIS2_BASE_RD + POS_GET_HI_OFFSET)
#define AXIS3_POS_GET_HI    (AXIS3_BASE_RD + POS_GET_HI_OFFSET)
#define AXIS4_POS_GET_HI    (AXIS4_BASE_RD + POS_GET_HI_OFFSET)

#define CMPLT_POS_OFFSET    0x2

#define AXIS0_CMPLT_POS     (AXIS0_BASE_RD + CMPLT_POS_OFFSET)
#define AXIS1_CMPLT_POS     (AXIS1_BASE_RD + CMPLT_POS_OFFSET)
#define AXIS2_CMPLT_POS     (AXIS2_BASE_RD + CMPLT_POS_OFFSET)
#define AXIS3_CMPLT_POS     (AXIS3_BASE_RD + CMPLT_POS_OFFSET)
#define AXIS4_CMPLT_POS     (AXIS4_BASE_RD + CMPLT_POS_OFFSET)

#define STATUS_SIG_OFFSET   0x3

#define AXIS0_STATUS_SIG    (AXIS0_BASE_RD + STATUS_SIG_OFFSET)
#define AXIS1_STATUS_SIG    (AXIS1_BASE_RD + STATUS_SIG_OFFSET)
#define AXIS2_STATUS_SIG    (AXIS2_BASE_RD + STATUS_SIG_OFFSET)
#define AXIS3_STATUS_SIG    (AXIS3_BASE_RD + STATUS_SIG_OFFSET)
#define AXIS4_STATUS_SIG    (AXIS4_BASE_RD + STATUS_SIG_OFFSET)

#define AXIS_STATUS_EMGS    (1<<15)
#define AXIS_STATUS_CRDY    (1<<14)
#define AXIS_STATUS_ZONE1   (1<<13)
#define AXIS_STATUS_ZONE2   (1<<12)
#define AXIS_STATUS_PZONE   (1<<11)
#define AXIS_STATUS_MODES   (1<<10)
#define AXIS_STATUS_WEND    (1<<9)
#define AXIS_STATUS_PSFL    (1<<5)
#define AXIS_STATUS_SV      (1<<4)
#define AXIS_STATUS_ALM     (1<<3)
#define AXIS_STATUS_MOVE    (1<<2)
#define AXIS_STATUS_HEND    (1<<1)
#define AXIS_STATUS_PEND    (1<<0)

#define LINACT_BUFLEN       (64)

#define TO_HEX(i) (i <= 9 : '0' + i ? 'A' - 10 + i)

namespace IAI {



  class LinActBuf {
    public:
        unsigned int len;
        unsigned char buf[LINACT_BUFLEN];
        char strbuf[LINACT_BUFLEN*2];
        void copy(LinActBuf &other);
        unsigned int crc_update(unsigned int crc, unsigned char a);
        void calc_crc();
        char *as_string();
        void readRegsisterStr(unsigned short startreg, unsigned short count);
        void writeRegisterStr(unsigned short reg, unsigned short value);
        void writeMultiRegisterStr(unsigned short reg,
            unsigned short reglen, unsigned char * data, unsigned char dlen);
  };

  class LinearActuator {

    public:
        LinActBuf buffer;
        LinearActuator();
        ~LinearActuator();
        unsigned short getAxisReadAddress(unsigned int axisid);
        unsigned short getAxisWriteAddress(unsigned int axisid);
        LinActBuf * getGwStatusStr();
        LinActBuf * getGwStartStr();
        LinActBuf * getAxisStatus(unsigned int axisid);
        LinActBuf * getAxisPos(unsigned int axisid);
        LinActBuf * getSetAxisPos(unsigned int axisid, unsigned int position);
  };

}



#endif /* LINACT_H */

