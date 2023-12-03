#include "define.h"
#include "function.h"
#include "port.h"

void setup()
{
  _setup();

//  digitalWrite(LED1,HIGH);
  dongservo(0);
  dongservo(1);
  while(!Serial);
}

unsigned long stimer=0; // sensor timer
unsigned long ktimer=0; // keypad timer


bool bservo[]={false,false};
bool birsensor[]={false,false,false,false};
unsigned long servo_timer[]={0,0}; // servo timer
unsigned long irsensor_timer[]={0,0,0,0}; // irsensor timer
bool bsv=false;

void loop()
{
  _loop();
  
  // doc du lieu tu may tinh
  while(Serial.available())
  {
    byte data=Serial.read();
    byte tp=data>>5;
//    if(tp==0b000) // type = value of irsensor's led
//    {
//      for(int i=0;i<3;i++)
//      {
//        batdenled(i,getbit(data,i));
//      }
//
//      
//    }
//    else if(tp==0b001)
//    {
//      for(int i=0;i<2;i++)
//      {
//        if(getbit(data,i))
//        {
//          moservo(i);
//          bservo[i]=true;
//          servo_timer[i]=millis();
//        }
////        else dongservo(i);
//      }
//    }
    if(tp==0b010)
    {
      for(int i=0;i<4;i++)
      {
        int j=i/2;
        if(getbit(data,i))
        {
          birsensor[i]=true;
          irsensor_timer[i]=millis();
          if(i==0||i==1)
          {
            batdenled(0,true);
            batdenled(1,true);
          }
          else // if(i==2||i==3)
          {
            batdenled(0,true);
            batdenled(2,true);
          }
          moservo(j);
          bservo[j]=true;
          servo_timer[j]=millis();
        }
      }
    }
  }


  // for(int i=0;i<4;i++)
  // {
  //   int j=i/2;

  //   if(birsensor[i])
  //   {
  //     if(!covatcan(i)) irsensor_timer[i]=millis();
  //     else if((unsigned long)(millis()-irsensor_timer[i])>1000) // neu co vat can dung 1s
  //     {
  //       dongservo(j);
  //       bservo[j]=false;
  //       birsensor[i]=false;
  //     }
  //   }
    
  //   // if(bservo[j]) // kiem tra neu servo thu j dang bat
  //   if(birsensor[i]) // kiem tra neu servo thu j dang bat
  //   {
  //     if((unsigned long)(millis()-servo_timer[j])>7500) // tu dong dong' servo sau moi 7.5s
  //     {
  //       dongservo(j);
  //       bservo[j]=false;
  //       birsensor[i]=false;
  //     }
  //   }
  // }
  
  // if(bsv)
  // {
  //   if((unsigned long)(millis()-servo_timer[0])>7500) // tu dong dong servo sau moi 7.5s
  //   {
  //     for(int i=0;i<2;i++) dongservo(i);
  //     bsv=false;
  //   }
  // }
  
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

  if((unsigned long)(millis()-servo_timer[0])>2000)
  {
    if(bsv) moservo(0);
    else dongservo(0);
    if(bsv) moservo(1);
    else dongservo(1);
    if(bsv) moservo(2);
    else dongservo(2);
    bsv=!bsv;
    servo_timer[0]=millis();
  }
  
  
//  delay(100);
  loop_();
}
