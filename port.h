#ifndef PORT_H
#define PORT_H

#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif


#include <string.h>

class // please do not create new instance with this type
{
private:
 String data="";
public:
 long baud=115200;
 void begin() { Serial.begin(baud); }
 void add(char val) { data+=val; }
 void write()
 {
   Serial.print(data);
   data="";
 }
 void end() { Serial.end(); }
 
} port;

















#endif // PORT_H
