/*
||
|| @file Keypad.h
|| @version 3.1
|| @author Mark Stanley, Alexander Brevig
|| @contact mstanley@technologist.com, alexanderbrevig@gmail.com
||
|| @description
|| | This library provides a simple interface for using matrix
|| | keypads. It supports multiple keypresses while maintaining
|| | backwards compatibility with the old single key library.
|| | It also supports user selectable pins and definable keymaps.
|| #
||
|| @license
|| | This library is free software; you can redistribute it and/or
|| | modify it under the terms of the GNU Lesser General Public
|| | License as published by the Free Software Foundation; version
|| | 2.1 of the License.
|| |
|| | This library is distributed in the hope that it will be useful,
|| | but WITHOUT ANY WARRANTY; without even the implied warranty of
|| | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
|| | Lesser General Public License for more details.
|| |
|| | You should have received a copy of the GNU Lesser General Public
|| | License along with this library; if not, write to the Free Software
|| | Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
|| #
||
*/


#ifndef Keypadlib_KEY_H_
#define Keypadlib_KEY_H_

#include <Arduino.h>

#define OPEN LOW
#define CLOSED HIGH

typedef unsigned int uint;
typedef enum{ IDLE, PRESSED, HOLD, RELEASED } KeyState;

// default value: \0 (0b0000)
// change it to 0b1111 just for compatible
const char NO_KEY = 0b1111;

class Key {
public:
	// members
	char kchar;
	int kcode;
	KeyState kstate;
	boolean stateChanged;

	// methods
	Key(){
		kchar = NO_KEY;
		kstate = IDLE;
		stateChanged = false;
	}
	Key(char userKeyChar){
		kchar = userKeyChar;
		kcode = -1;
		kstate = IDLE;
		stateChanged = false;
	}
	void key_update(char userKeyChar, KeyState userState, boolean userStatus){
		kchar = userKeyChar;
		kstate = userState;
		stateChanged = userStatus;
	}

private:

};

#endif

#ifndef KEYPAD_H
#define KEYPAD_H

// #include "Key.h"

// bperrybap - Thanks for a well reasoned argument and the following macro(s).
// See http://arduino.cc/forum/index.php/topic,142041.msg1069480.html#msg1069480
#ifndef INPUT_PULLUP
#warning "Using  pinMode() INPUT_PULLUP AVR emulation"
#define INPUT_PULLUP 0x2
#define pinMode(_pin, _mode) _mypinMode(_pin, _mode)
#define _mypinMode(_pin, _mode)  \
do {							 \
	if(_mode == INPUT_PULLUP)	 \
		pinMode(_pin, INPUT);	 \
		digitalWrite(_pin, 1);	 \
	if(_mode != INPUT_PULLUP)	 \
		pinMode(_pin, _mode);	 \
}while(0)
#endif


#define OPEN LOW
#define CLOSED HIGH

typedef char KeypadEvent;
typedef unsigned int uint;
typedef unsigned long ulong;

// Made changes according to this post http://arduino.cc/forum/index.php?topic=58337.0
// by Nick Gammon. Thanks for the input Nick. It actually saved 78 bytes for me. :)
typedef struct {
    byte rows;
    byte columns;
} KeypadSize;

#define LIST_MAX 10		// Max number of keys on the active list.
#define MAPSIZE 10		// MAPSIZE is the number of rows (times 16 columns)
#define makeKeymap(x) ((char*)x)


//class Keypad : public Key, public HAL_obj {
class Keypad : public Key {
public:

	Keypad(char *userKeymap, byte *row, byte *col, byte numRows, byte numCols){
		rowPins = row;
		columnPins = col;
		sizeKpd.rows = numRows;
		sizeKpd.columns = numCols;

		begin(userKeymap);

		setDebounceTime(10);
		setHoldTime(500);
		keypadEventListener = 0;

		startTime = 0;
		single_key = false;
	}

	virtual void pin_mode(byte pinNum, byte mode) { pinMode(pinNum, mode); }
	virtual void pin_write(byte pinNum, boolean level) { digitalWrite(pinNum, level); }
	virtual int  pin_read(byte pinNum) { return digitalRead(pinNum); }

	uint bitMap[MAPSIZE];	// 10 row x 16 column array of bits. Except Due which has 32 columns.
	Key key[LIST_MAX];
	unsigned long holdTimer;

	char getKey(){
		single_key = true;

		if (getKeys() && key[0].stateChanged && (key[0].kstate==PRESSED))
			return key[0].kchar;
		
		single_key = false;

		return NO_KEY;
	}
	bool getKeys(){
		bool keyActivity = false;

		// Limit how often the keypad is scanned. This makes the loop() run 10 times as fast.
		if ( (millis()-startTime)>debounceTime ) {
			scanKeys();
			keyActivity = updateList();
			startTime = millis();
		}

		return keyActivity;
	}
	KeyState getState(){
		return key[0].kstate;
	}
	void begin(char *userKeymap){
		keymap = userKeymap;
	}
	bool isPressed(char keyChar){
		for (byte i=0; i<LIST_MAX; i++) {
			if ( key[i].kchar == keyChar ) {
				if ( (key[i].kstate == PRESSED) && key[i].stateChanged )
					return true;
			}
		}
		return false;	// Not pressed.
	}
	void setDebounceTime(uint debounce){
		debounce<1 ? debounceTime=1 : debounceTime=debounce;
	}
	void setHoldTime(uint hold){
	    holdTime = hold;
	}
	void addEventListener(void (*listener)(char)){
		keypadEventListener = listener;
	}
	int findInList(char keyChar){
		for (byte i=0; i<LIST_MAX; i++) {
			if (key[i].kchar == keyChar) {
				return i;
			}
		}
		return -1;
	}
	int findInList(int keyCode){
		for (byte i=0; i<LIST_MAX; i++) {
			if (key[i].kcode == keyCode) {
				return i;
			}
		}
		return -1;
	}
	char waitForKey(){
		char waitKey = NO_KEY;
		while( (waitKey = getKey()) == NO_KEY );	// Block everything while waiting for a keypress.
		return waitKey;
	}
	bool keyStateChanged(){
		return key[0].stateChanged;
	}
	byte numKeys(){
		return sizeof(key)/sizeof(Key);
	}
private:
	unsigned long startTime;
	char *keymap;
    byte *rowPins;
    byte *columnPins;
	KeypadSize sizeKpd;
	uint debounceTime;
	uint holdTime;
	bool single_key;

	void scanKeys(){
		// Re-intialize the row pins. Allows sharing these pins with other hardware.
		for (byte r=0; r<sizeKpd.rows; r++) {
			pin_mode(rowPins[r],INPUT_PULLUP);
		}

		// bitMap stores ALL the keys that are being pressed.
		for (byte c=0; c<sizeKpd.columns; c++) {
			pin_mode(columnPins[c],OUTPUT);
			pin_write(columnPins[c], LOW);	// Begin column pulse output.
			for (byte r=0; r<sizeKpd.rows; r++) {
				bitWrite(bitMap[r], c, !pin_read(rowPins[r]));  // keypress is active low so invert to high.
			}
			// Set pin to high impedance input. Effectively ends column pulse.
			pin_write(columnPins[c],HIGH);
			pin_mode(columnPins[c],INPUT);
		}
	}
	bool updateList(){

		bool anyActivity = false;

		// Delete any IDLE keys
		for (byte i=0; i<LIST_MAX; i++) {
			if (key[i].kstate==IDLE) {
				key[i].kchar = NO_KEY;
				key[i].kcode = -1;
				key[i].stateChanged = false;
			}
		}

		// Add new keys to empty slots in the key list.
		for (byte r=0; r<sizeKpd.rows; r++) {
			for (byte c=0; c<sizeKpd.columns; c++) {
				boolean button = bitRead(bitMap[r],c);
				char keyChar = keymap[r * sizeKpd.columns + c];
				int keyCode = r * sizeKpd.columns + c;
				int idx = findInList (keyCode);
				// Key is already on the list so set its next state.
				if (idx > -1)	{
					nextKeyState(idx, button);
				}
				// Key is NOT on the list so add it.
				if ((idx == -1) && button) {
					for (byte i=0; i<LIST_MAX; i++) {
						if (key[i].kchar==NO_KEY) {		// Find an empty slot or don't add key to list.
							key[i].kchar = keyChar;
							key[i].kcode = keyCode;
							key[i].kstate = IDLE;		// Keys NOT on the list have an initial state of IDLE.
							nextKeyState (i, button);
							break;	// Don't fill all the empty slots with the same key.
						}
					}
				}
			}
		}

		// Report if the user changed the state of any key.
		for (byte i=0; i<LIST_MAX; i++) {
			if (key[i].stateChanged) anyActivity = true;
		}

		return anyActivity;
	}
	void nextKeyState(byte idx, boolean button){
		key[idx].stateChanged = false;

		switch (key[idx].kstate) {
			case IDLE:
				if (button==CLOSED) {
					transitionTo (idx, PRESSED);
					holdTimer = millis(); }		// Get ready for next HOLD state.
				break;
			case PRESSED:
				if ((millis()-holdTimer)>holdTime)	// Waiting for a key HOLD...
					transitionTo (idx, HOLD);
				else if (button==OPEN)				// or for a key to be RELEASED.
					transitionTo (idx, RELEASED);
				break;
			case HOLD:
				if (button==OPEN)
					transitionTo (idx, RELEASED);
				break;
			case RELEASED:
				transitionTo (idx, IDLE);
				break;
		}
	}
	void transitionTo(byte idx, KeyState nextState){
		key[idx].kstate = nextState;
		key[idx].stateChanged = true;

		// Sketch used the getKey() function.
		// Calls keypadEventListener only when the first key in slot 0 changes state.
		if (single_key)  {
		  	if ( (keypadEventListener!=NULL) && (idx==0) )  {
				keypadEventListener(key[0].kchar);
			}
		}
		// Sketch used the getKeys() function.
		// Calls keypadEventListener on any key that changes state.
		else {
		  	if (keypadEventListener!=NULL)  {
				keypadEventListener(key[idx].kchar);
			}
		}
	}
	void (*keypadEventListener)(char);
};

#endif

/*
|| @changelog
|| | 3.1 2013-01-15 - Mark Stanley     : Fixed missing RELEASED & IDLE status when using a single key.
|| | 3.0 2012-07-12 - Mark Stanley     : Made library multi-keypress by default. (Backwards compatible)
|| | 3.0 2012-07-12 - Mark Stanley     : Modified pin functions to support Keypad_I2C
|| | 3.0 2012-07-12 - Stanley & Young  : Removed static variables. Fix for multiple keypad objects.
|| | 3.0 2012-07-12 - Mark Stanley     : Fixed bug that caused shorted pins when pressing multiple keys.
|| | 2.0 2011-12-29 - Mark Stanley     : Added waitForKey().
|| | 2.0 2011-12-23 - Mark Stanley     : Added the public function keyStateChanged().
|| | 2.0 2011-12-23 - Mark Stanley     : Added the private function scanKeys().
|| | 2.0 2011-12-23 - Mark Stanley     : Moved the Finite State Machine into the function getKeyState().
|| | 2.0 2011-12-23 - Mark Stanley     : Removed the member variable lastUdate. Not needed after rewrite.
|| | 1.8 2011-11-21 - Mark Stanley     : Added test to determine which header file to compile,
|| |                                          WProgram.h or Arduino.h.
|| | 1.8 2009-07-08 - Alexander Brevig : No longer uses arrays
|| | 1.7 2009-06-18 - Alexander Brevig : This library is a Finite State Machine every time a state changes
|| |                                          the keypadEventListener will trigger, if set
|| | 1.7 2009-06-18 - Alexander Brevig : Added setDebounceTime setHoldTime specifies the amount of
|| |                                          microseconds before a HOLD state triggers
|| | 1.7 2009-06-18 - Alexander Brevig : Added transitionTo
|| | 1.6 2009-06-15 - Alexander Brevig : Added getState() and state variable
|| | 1.5 2009-05-19 - Alexander Brevig : Added setHoldTime()
|| | 1.4 2009-05-15 - Alexander Brevig : Added addEventListener
|| | 1.3 2009-05-12 - Alexander Brevig : Added lastUdate, in order to do simple debouncing
|| | 1.2 2009-05-09 - Alexander Brevig : Changed getKey()
|| | 1.1 2009-04-28 - Alexander Brevig : Modified API, and made variables private
|| | 1.0 2007-XX-XX - Mark Stanley : Initial Release
|| #
*/
