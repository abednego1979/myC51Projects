/********************************************************
translate grbl signal to 35byj-46
*********************************************************/
#include <reg52.h>

/*
********************************
 GRBL to 35BYJ-46 Step Motor
x step            P0^0    up edge valid default
x direct        P0^1    
y step            P0^2    up edge valid default
y direct        P0^3    
z step            P0^4    up edge valid default
z direct        P0^5    
step enable        P0^6    
            
output signals:            
steperx_A    P1^0        
steperx_B    P1^1        
steperx_C    P1^2        
steperx_D    P1^3        
stepery_A    P1^4        
stepery_B    P1^5        
stepery_C    P1^6        
stepery_D    P1^7        
            
steperz_A    P2^0        
steperz_B    P2^1        
steperz_C    P2^2        
steperz_D    P2^3    
********************************
*/

#define uchar unsigned char
#define uint unsigned int

#define STEPER_MOTO_TYPE        "35BYJ46-ULN2003"

#if STEPER_MOTO_TYPE=="35BYJ46-ULN2003"
uchar step_format[8]={0x01,0x03,0x02,0x06,0x04,0x0C,0x08,0x09};
uchar step_disable_format=0x00;
#else
#error "Unknown Moto type"
#endif
uchar x_index=0;
uchar y_index=0;
uchar z_index=0;
uchar spindle_en=0;

uchar last_moving_axis=0; /*0-X, 1-Y, 2-Y*/


/*input signal(From P1)*/
#define STEP_X_STATE ((input>>0)&0x1)
#define STEP_Y_STATE ((input>>1)&0x1)
#define STEP_Z_STATE ((input>>2)&0x1)
#define DIR_X_STATE ((input>>3)&0x1)
#define DIR_Y_STATE ((input>>4)&0x1)
#define DIR_Z_STATE ((input>>5)&0x1)
#define STEP_ENABLE_FLAG ((input>>6)&0x1)
#define SPINDLE_ENABLE ((input>>7)&0x1)

/*output signal*/
/*
MOTO X: A-B-C-D: P0.0-P0.1-P0.2-P0.3
MOTO Y: A-B-C-D: P0.4-P0.5-P0.6-P0.7
MOTO Z: A-B-C-D: P2.7-P2.6-P2.5-P2.4
Spindle Enable: P2.3
*/

#define INVERT_4BIT(x) (((x<<3)&0x08)|((x<<1)&0x04)|((x>>1)&0x02)|((x>>3)&0x01))

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

void CtrlSignalOutput(uchar steper_en)
{   
    if (steper_en)
    {
        P0=(step_format[y_index]<<4)|(step_format[x_index]&0x0F);
        P2=(INVERT_4BIT(step_format[z_index])<<4)|(spindle_en<<3);
    }
    else:
    {
        P0=(step_disable_format<<4)|(step_disable_format&0x0F);
        P2=(INVERT_4BIT(step_disable_format)<<4)|(spindle_en<<3);
    }
}

void main(void)
{
    uchar old_step_x=0;
    uchar old_step_y=0;
    uchar old_step_z=0;
    uchar input;
    uchar new_step_x,new_step_y,new_step_z;
    
    P0=0x00;
    P1=0xFF;
    P2=0x00;

    while (1)
    {
        P1=0xFF;
        delayShort(2);
        input = P1;
        
        
    new_step_x=STEP_X_STATE;
    new_step_y=STEP_Y_STATE;
    new_step_z=STEP_Z_STATE;
            
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
        last_moving_axis=0;
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
        last_moving_axis=1;
    }
    old_step_y=new_step_y;

    if ((old_step_z==0)&&(new_step_z==1))
    {
        if (DIR_Z_STATE)
        {
        z_index=(z_index+1)%8;
        }
        else
        {
        z_index=(z_index+7)%8;
        }
        last_moving_axis=2;
    }
    old_step_z=new_step_z;

    spindle_en=SPINDLE_ENABLE;/*如果Spindle_en需要反相，在这里做*/

            
    CtrlSignalOutput(STEP_ENABLE_FLAG);
    }
}

