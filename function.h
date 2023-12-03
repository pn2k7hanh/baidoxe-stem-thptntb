#ifndef FUNCTION_H
#define FUNCTION_H

#include "define.h"
#include "port.h"

#define getbit(a,n) ((a&(1<<n))?1:0) // get n th bit of binary a
#define setbit(a,n,v) (v?(a|=(1<<n)):(a&=(~(1<<n)))) // set n th bit of binary a to value v and return new value

void _setup(); // chay truoc khi bat dau ham setup
void _loop(); // chay truoc khi bat dau vong loop
void loop_(); // chay sau khi bat dau vong loop

// Servo
#define CUAMO 1
#define CUADONG 0
void moservo(int);
void dongservo(int);
bool trangthaiservo(int);

// Gas Sensor
//#define COKHOI 1
//#define KHONGCOKHOI 0
//bool cokhoi();
//byte luongkhoi();

// Flame Sensor
#define COLUA LOW
#define KHONCOLUA HIGH
byte lua();
bool colua();

// IR Sensor
#define COVATCAN LOW
#define KHONGCOVATCAN HIGH
bool covatcan(int);

// port
void send_gassensor();
void send_irsensor();
void send_keypad(byte);

// LED
void batdenled(int,bool);
void bathetdenled(bool);

void _setup()
{
  Serial.begin(115200); // for communication with extended program on computer

//  Su dung buzzer/loa
  // pinMode(BUZZER,OUTPUT);

//  Su dung cam bien khoang cach hong ngoai
  pinMode(IRSENSOR1,INPUT);
  pinMode(IRSENSOR2,INPUT);
  pinMode(IRSENSOR3,INPUT);
  pinMode(IRSENSOR4,INPUT);
  
// led 1 la duong o giua
// led 2 la chi dan ben trai
// led 3 la chi dan ben phai
  pinMode(LED1,OUTPUT);
  pinMode(LED2,OUTPUT);
  pinMode(LED3,OUTPUT);


//  Su dung cam bien khoang cach sieu am
//  pinMode(HCSENSORA,INPUT);
//  pinMode(HCSENSORD,INPUT);

//  Su dung cac servo1, servo2, servo3
//  servo1 dung cho cua khu A
//  servo2 dung cho cua khu B
  servo[0].attach(SERVO1);
  servo[1].attach(SERVO2);
  servo[2].attach(SERVO3);

  

  
}


void _loop()
{
  
}


void loop_()
{
  
}

void moservo(int cua=0)
{
  servo[cua].write(90);
}

void dongservo(int cua=0)
{
  servo[cua].write(0);
}

bool trangthaiservo(int cua=0)
{
  return (servo[cua].read()>80);
}




//bool cokhoi()
//{
//  return (analogRead(GASSENSOR)>80);
//}
//
//byte luongkhoi()
//{
//  return map(min(analogRead(GASSENSOR),512),0,512,0,31);
//}

byte lua()
{
  return map(min(analogRead(FLAMESENSOR),512),0,512,0,31);
}

bool colua()
{
  return (digitalRead(FLAMESENSOR)==COLUA);
}

bool covatcan(int ir=0)
{
  return (digitalRead(irsensor[ir])==COVATCAN);
}

void batdenled(int n,bool check)
{
  if(check) digitalWrite(led[n],HIGH);
  else digitalWrite(led[n],LOW);
}
void bathetdenled(bool check)
{
  for(int i=0;i<3;i++)
  {
    batdenled(i,check);
  }
}

void send_irsensor()
{
  byte data=0b00000000;
  for(byte i=0;i<4;i++)
  {
    if(covatcan(i))
    {
      data+=(1<<i);
    }
  }
  port.add(data);
}

//void send_gassensor()
//{
//  byte val=luongkhoi();
//  byte data=0b00010000;
//  data+=val;
//  port.add(data);
//}

void send_flamesensor()
{
  byte data=0b00100000;
  // byte val=lua();
  // data+=val;
  if(colua()) data+=0b1;
  port.add(data);
}

void send_keypad(byte val)
{
  byte data=0b01100000;
  data+=val;
  port.add(data);
}














#endif // FUNCTION_H
