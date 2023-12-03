#ifndef DEFINE_H
#define DEFINE_H

// Cam bien vat can
#define IRSENSOR1 2
#define IRSENSOR2 3
#define IRSENSOR3 4
#define IRSENSOR4 5
byte irsensor[]={IRSENSOR1,IRSENSOR2,IRSENSOR3,IRSENSOR4};

// Den led de chi duong
#define LED1 6
#define LED2 7
#define LED3 8
byte led[]={LED1,LED2,LED3};


// AM THANH
// #define BUZZER A5


//// CAM BIEN KHOI (CO2)
//#define GASSENSOR A3

// CAM BIEN LUA(FLAME)
#define FLAMESENSOR A4


// SERVO
#define SERVO1 9
#define SERVO2 10
#define SERVO3 A5
#include <Servo.h>
Servo servo[3];

// Ban phim mem 4x4
#include "Keypad.h"
#define KROWS 4
#define KCOLS 3

//  {'1','2','3'},
//  {'4','5','6'},
//  {'7','8','9'},
//  {'*','0','#'}

char keys[KROWS][KCOLS]={
  {0b0000,0b0001,0b0010},
  {0b0100,0b0101,0b0110},
  {0b1000,0b1001,0b1010},
  {0b1100,0b1101,0b1110}
};

byte krows[KROWS]={A3,A2,A1,A0};
byte kcols[KCOLS]={11,12,13};
Keypad kpad(makeKeymap(keys),krows,kcols,KROWS,KCOLS);












#endif // DEFINE_H
