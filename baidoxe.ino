#include "define.h"
#include "function.h"
#include "port.h"

void setup()
{
  _setup();

//  digitalWrite(LED1,HIGH);
  
  while(!Serial);
}

unsigned long stimer=0; // sensor timer
unsigned long ktimer=0; // keypad timer

bool bservo=false;
unsigned long servo_timer=0; // servo timer
//byte servo;

void loop()
{
  _loop();
  
  // doc du lieu tu may tinh
  while(Serial.available())
  {
    byte data=Serial.read();
    byte tp=data>>5;
    if(tp==0b000) // type = value of irsensor's led
    {
      for(int i=0;i<3;i++)
      {
        batdenled(i,getbit(data,i));
      }

      
    }
    else if(tp==0b001)
    {
      for(int i=0;i<2;i++)
      {
        if(getbit(data,i))
        {
          moservo(i);
          bservo=true;
          servo_timer=millis();
        }
        else dongservo(i);
      }
    }
  }

  if(bservo)
  {
   if((unsigned long)(millis()-servo_timer)>5000)
   {
    for(int i=0;i<2;i++) dongservo(i);
    bservo=false;
   }
  }
  
  // doc tin hieu tu ban phim 4x4 sau moi 0.25 giay
  if((unsigned long)(millis()-ktimer)>250)
  {
   char key=kpad.getKey();
   if(key!=NO_KEY)
   {
     send_keypad(key);
     port.write();
   }
   ktimer=millis();
  }
  


  // gui du lieu tu cam bien den may tinh sau moi 1 giay
  if((unsigned long)(millis()-stimer)>1000)
  {
    send_irsensor();
    send_flamesensor();
    port.write();
    
    stimer=millis();
  }

//  if((unsigned long)(millis()-servo_timer)>2000)
//  {
//    if(bservo) moservo();
//    else dongservo();
//    bservo=!bservo;
//    servo_timer=millis();
//  }
  
  
//  delay(100);
  loop_();
}
