/********************************************************
translate grbl signal to 35byj-46
*********************************************************/
#include <reg52.h>

/*
********************************
 GRBL to 35BYJ-46 Step Motor
 GRBL x step          <--> P1^0	up edge valid default
 GRBL x direct        <--> P1^1
 GRBL y step          <--> P1^2	up edge valid default
 GRBL y direct        <--> P1^3
 GRBL step enable     <--> P1^4 no used
 GRBL splindle enable <--> P1^5
 
 STEP 1_A    <--> P2^0
 STEP 1_B    <--> P2^1
 STEP 1_C    <--> P2^2
 STEP 1_D    <--> P2^3
 STEP 2_A    <--> P2^4
 STEP 2_B    <--> P2^5
 STEP 2_C    <--> P2^6
 STEP 2_D    <--> P2^7
********************************
*/

#define uchar unsigned char
#define uint unsigned int

uchar step_format[8]={0x1,0x3,0x2,0x6,0x4,0xC,0x8,0x9};
uchar x_index=0;
uchar y_index=0;

#define DIR_X_STATE ((input>>1)&0x1)
#define STEP_X_STATE ((input>>0)&0x1)
#define DIR_Y_STATE ((input>>3)&0x1)
#define STEP_Y_STATE ((input>>2)&0x1)
#define STEP_ENABLE_FLAG ((input>>4)&0x1)	/*no used*/
#define SPLINDLE_ENABLE_FLAG ((input>>5)&0x1)

void delayShort(uchar ucDelayTime)
{
    uchar ui=0;
    uchar ucCnti;
    for(ui=0; ui<ucDelayTime ; ui++)
    {
        for(ucCnti=0; ucCnti<5 ; ucCnti++)
        {    
        }    
    }
}

void P2Output()
{
    P2=(step_format[y_index]<<4)|(step_format[x_index]&0x0F);
}

void main(void)
{
    uchar old_step_x=0;
    uchar old_step_y=0;
    uchar input;
    uchar new_step_x,new_step_y;
    

    P0=0xFF;
    P1=0xFF;
    P2=0x00;

    while (1)
    {
        P1=0xFF;
        delayShort(2);
        input = P1;
        
	new_step_x=STEP_X_STATE;
	new_step_y=STEP_Y_STATE;
            
	if ((old_step_x==0)&&(new_step_x==1))
	{
	    if (DIR_X_STATE)
	    {
		x_index=(x_index+1)%8;
	    }
	    else
	    {
		x_index=(x_index+7)%8;
	    }
	}
	old_step_x=new_step_x;
            
            
	if ((old_step_y==0)&&(new_step_y==1))
	{
	    if (DIR_Y_STATE)
	    {
		y_index=(y_index+1)%8;
	    }
	    else
	    {
		y_index=(y_index+7)%8;
	    }
	}
	old_step_y=new_step_y;
            
	P2Output();
    }
}

