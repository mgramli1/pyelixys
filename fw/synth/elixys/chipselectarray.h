#ifndef CHIPSELECT_H
#define CHIPSELECT_H
#include "mbed.h"
#include "ShiftRegister.h"

#define FIRST2LAST(X) (31 - (X))
#define VALVCS0  ~(1U << FIRST2LAST(0))
#define VALVCS1  ~(1U << FIRST2LAST(1))
#define VALVCS2  ~(1U << FIRST2LAST(2))
#define THERMCOUPLECS0 ~(1U << FIRST2LAST(3))
#define THERMCOUPLECS1 ~(1U << FIRST2LAST(4))
#define THERMCOUPLECS2 ~(1U << FIRST2LAST(5))
#define THERMCOUPLECS3 ~(1U << FIRST2LAST(6))
#define THERMCOUPLECS4 ~(1U << FIRST2LAST(7))
#define THERMCOUPLECS5 ~(1U << FIRST2LAST(8))
#define THERMCOUPLECS6 ~(1U << FIRST2LAST(9))
#define THERMCOUPLECS7 ~(1U << FIRST2LAST(10))
#define THERMCOUPLECS8 ~(1U << FIRST2LAST(11))
#define HEATERCS ~(1U << FIRST2LAST(12))
#define LIQUIDSENSORCS ~(1U << FIRST2LAST(13))
#define POSITIONSENSORCS ~(1U << FIRST2LAST(14))
#define SMCADCCS ~(1U << FIRST2LAST(15))
#define SMCDACCS ~(1U << FIRST2LAST(16))
#define RADCS0 ~(1U << FIRST2LAST(17))
#define RADCS1 ~(1U << FIRST2LAST(18))
#define RADCS2 ~(1U << FIRST2LAST(19))
#define RADCS3 ~(1U << FIRST2LAST(20))
#define RADCS4 ~(1U << FIRST2LAST(21))
#define RADCS5 ~(1U << FIRST2LAST(22))
#define RADCS6 ~(1U << FIRST2LAST(23))
#define AUXCS0 ~(1U << FIRST2LAST(24))
#define AUXCS1 ~(1U << FIRST2LAST(25))
#define AUXCS2 ~(1U << FIRST2LAST(26))
#define AUXCS3 ~(1U << FIRST2LAST(27))
#define AUXCS4 ~(1U << FIRST2LAST(28))
#define AUXCS5 ~(1U << FIRST2LAST(29))
#define AUXCS6 ~(1U << FIRST2LAST(30))
#define AUXCS7 ~(1U << FIRST2LAST(31))
#define NONECS ~(0x00000000)


void unselect(void);
void selectvalve0(void);
void selectvalve1(void);
void selectvalve2(void);
void selecttc0(void);
void selecttc1(void);
void selecttc2(void);
void selecttc3(void);
void selecttc4(void);
void selecttc5(void);
void selecttc6(void);
void selecttc7(void);
void selecttc8(void);
void selectheater(void);
void selectliq(void);
void selectpos(void);
void selectsmcadc(void);
void selectsmcdac(void);
void selectrad0(void);
void selectrad1(void);
void selectrad2(void);
void selectrad3(void);
void selectrad4(void);
void selectrad5(void);
void selectrad6(void);
void selectaux0(void);
void selectaux1(void);
void selectaux2(void);
void selectaux3(void);
void selectaux4(void);
void selectaux5(void);
void selectaux6(void);
void selectaux7(void);

#endif //CHIPSELECT_H