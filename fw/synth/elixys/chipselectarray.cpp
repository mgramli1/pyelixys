#include "chipselectarray.h"

DigitalOut cssck(P1_20);
DigitalOut csdat(P1_24);
DigitalOut cslatch(P1_21);
DigitalOut csclr(P1_22);
DigitalOut csoe(P1_25);
ShiftRegister shiftreg(cssck, csdat, cslatch, csclr, csoe);

void unselect() {
    shiftreg.write((unsigned int)NONECS, 32);
}

void selectvalve0(void) {
    shiftreg.write((unsigned int)VALVCS0, 32);
}

void selectvalve1(void) {
    shiftreg.write((unsigned int)VALVCS1, 32);
}

void selectvalve2(void) {
    shiftreg.write((unsigned int)VALVCS2, 32);
}

void selecttc0() {
    shiftreg.write((unsigned int)THERMCOUPLECS0, 32);
}

void selecttc1() {
    shiftreg.write((unsigned int)THERMCOUPLECS1, 32);
}

void selecttc2() {
    shiftreg.write((unsigned int)THERMCOUPLECS2, 32);
}

void selecttc3(void) {
    shiftreg.write((unsigned int)THERMCOUPLECS3, 32);
}

void selecttc4() {
    shiftreg.write((unsigned int)THERMCOUPLECS4, 32);
}

void selecttc5() {
    shiftreg.write((unsigned int)THERMCOUPLECS5, 32);
}

void selecttc6() {
    shiftreg.write((unsigned int)THERMCOUPLECS6, 32);
}

void selecttc7() {
    shiftreg.write((unsigned int)THERMCOUPLECS7, 32);
}

void selecttc8() {
    shiftreg.write((unsigned int)THERMCOUPLECS8, 32);
}

void selectheater(void) {
    shiftreg.write((unsigned int)HEATERCS, 32);
}

void selectliq(void) {
    shiftreg.write((unsigned int)LIQUIDSENSORCS, 32);
}

void selectpos(void) {
    shiftreg.write((unsigned int)POSITIONSENSORCS, 32);
}

void selectsmcadc(void) {
    shiftreg.write((unsigned int)SMCADCCS, 32);
}

void selectsmcdac(void) {
    shiftreg.write((unsigned int)SMCDACCS, 32);
}

void selectrad0(void) {
    shiftreg.write((unsigned int)RADCS0, 32);
}

void selectrad1(void) {
    shiftreg.write((unsigned int)RADCS1, 32);
}

void selectrad2(void) {
    shiftreg.write((unsigned int)RADCS2, 32);
}

void selectrad3(void) {
    shiftreg.write((unsigned int)RADCS3, 32);
}

void selectrad4(void) {
    shiftreg.write((unsigned int)RADCS4, 32);
}

void selectrad5(void) {
    shiftreg.write((unsigned int)RADCS5, 32);
}

void selectrad6(void) {
    shiftreg.write((unsigned int)RADCS6, 32);
}

void selectaux0(void) {
    shiftreg.write((unsigned int)AUXCS0, 32);
}

void selectaux1(void) {
    shiftreg.write((unsigned int)AUXCS1, 32);
}

void selectaux2(void) {
    shiftreg.write((unsigned int)AUXCS2, 32);
}

void selectaux3(void) {
    shiftreg.write((unsigned int)AUXCS3, 32);
}

void selectaux4(void) {
    shiftreg.write((unsigned int)AUXCS4, 32);
}

void selectaux5(void) {
    shiftreg.write((unsigned int)AUXCS5, 32);
}

void selectaux6(void) {
    shiftreg.write((unsigned int)AUXCS6, 32);
}

void selectaux7(void){
    shiftreg.write((unsigned int)AUXCS7, 32);
}
