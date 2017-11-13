/********************************************************
PC send text to set or get MCU port.

Protocal:
PC----------------MCU

set port
    ----Spxx---->           
    <----S----
    
get port
    ----Gp---->
    <----Gxx----
    
reset MCU data buffer
    ----X---->
    <----RESET----
    
MCU report Error to PC
    <----E----

p=0/1/2
xx=Hex num like 6B
*********************************************************/
#include <reg52.h>


#define uchar unsigned char
#define uint unsigned int

#define SET_MESSAGE_LEN    4
#define GET_MESSAGE_LEN    2

#define SERIAL_RCV_BUF_LEN 32
uchar Receive_Buffer[SERIAL_RCV_BUF_LEN]={0};
uchar Buf_Index;

void Serial_trans_String(char *pStr);



/*serial port receive func*/
void Serial_INT() interrupt 4
{
    uchar c;
    if(RI==0) return;
    ES=0; //close serial port interrupt
    RI=0; //clear port interrupt flag
    c=SBUF;

    if(Buf_Index<(SERIAL_RCV_BUF_LEN-1))
    {
        Receive_Buffer[Buf_Index]=c;
        Buf_Index++;
    }
    else
    {
        Serial_trans_String("E");
        Buf_Index=0;    
    }

    ES=1;    //re-open port interrupt
}

void Serial_trans(uchar ucOut)
{

    SBUF = ucOut;
    while(TI==0);
    TI=0;
}

uchar Char2Data(uchar ucChar)
{
    if((ucChar>='a')&&(ucChar<='f'))
    {
        return (ucChar-'a'+10);
    }

    if((ucChar>='A')&&(ucChar<='F'))
    {
        return (ucChar-'A'+10);
    }

    if((ucChar>='0')&&(ucChar<='9'))
    {
        return (ucChar-'0');
    }

    return 0;
}

void Serial_trans_String(char *pStr)
{
    while(*pStr != 0)
    {
        Serial_trans(*pStr);
        pStr++;
    }
}

uchar Data2Char1(uchar ucData)
{
    ucData = ucData>>4;
    
    if((ucData>=0)&&(ucData<=9))
    {
        return '0'+ucData;
    }
    else
    {
        return 'A'+ucData-10;
    }
}

uchar Data2Char0(uchar ucData)
{
    ucData = ucData&0x0F;
    
    if((ucData>=0)&&(ucData<=9))
    {
        return '0'+ucData;
    }
    else
    {
        return 'A'+ucData-10;
    }
}

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

void recvProc()
{
    if (0==Buf_Index)
    {
        return;
    }

    if(Receive_Buffer[0] == 'S')
    {
        /*set port*/
        if(Buf_Index>=SET_MESSAGE_LEN)
        {
            uchar portindex = Char2Data(Receive_Buffer[1]);
            uchar ucDate1 = Char2Data(Receive_Buffer[2]);
            uchar ucDate0 = Char2Data(Receive_Buffer[3]);
            uchar ui;

            uchar ucData = (ucDate1<<4)|(ucDate0&0x0f);

            if (portindex==0)
            {
                //P0
                P0=ucData;                    
            }
            else if (portindex==1)
            {                 
                //P1
                P1=ucData;                    
            }
            else if (portindex==2)
            {                  
                //P2
                P2=ucData;                    
            }
            else
            {
                Serial_trans_String("E");
                Buf_Index=0;
            }
            ES=0; //close serial port interrupt
            for(ui=0; ui<(SERIAL_RCV_BUF_LEN-SET_MESSAGE_LEN); ui++)
            {
                Receive_Buffer[ui] = Receive_Buffer[ui+SET_MESSAGE_LEN];    
            }
            if (Buf_Index>=SET_MESSAGE_LEN)
            {
                Buf_Index-=SET_MESSAGE_LEN;
            }
            ES=1;    //re-open port interrupt


            Serial_trans_String("S");
        }
    }
    else if(Receive_Buffer[0] == 'G')
    {
        /*get port*/
        if(Buf_Index>=GET_MESSAGE_LEN)
        {
            uchar portindex = Char2Data(Receive_Buffer[1]);
            uchar ui;

            uchar ucData;

            if (portindex==0)
            {
                //P0
                P0=0xFF;
                delayShort(2);

                ucData = P0;
                                    
            }
            else if (portindex==1)
            {                 
                //P1
                P1=0xFF;
                delayShort(2);

                ucData = P1;                    
            }
            else if (portindex==2)
            {                  
                //P2
                P2=0xFF;
                delayShort(2);

                ucData = P2;                    
            }
            else
            {
                Buf_Index=0;
                Serial_trans_String("E");
            }
            ES=0; //close serial port interrupt
            for(ui=0; ui<(SERIAL_RCV_BUF_LEN-GET_MESSAGE_LEN); ui++)
            {
                Receive_Buffer[ui] = Receive_Buffer[ui+GET_MESSAGE_LEN];    
            }
            if (Buf_Index>=GET_MESSAGE_LEN)
            {
                Buf_Index-=GET_MESSAGE_LEN;
            }
            ES=1;    //re-open port interrupt


            Serial_trans_String("G");
            Serial_trans(Data2Char1(ucData));
            Serial_trans(Data2Char0(ucData));
        }    
    }
    else if(Receive_Buffer[0] == 'X')
    {
        /*Reset*/
        Buf_Index=0;
        Serial_trans_String("RESET");
    }
    else
    {
        Serial_trans_String("E");
        Buf_Index=0;

    }

}

void main(void)
{
    P1=0xF0;
    P2=0x00;
    SCON=0x50; /*serial port mode 1, receive is enable*/
    TMOD=0x20; /*Timer1 work mode 2*/
    TH1=0xfd; /*Band Rate 9600*/
    TL1=0xfd;
    PCON=0x00; /*Band Rate do not redouble*/
    EA=1;EX0=0;IT0=1;
    ES=1;IP=0x01;
    TR1=1;

    IT1=1;

    Serial_trans_String("\r\n");
    Serial_trans_String("********************************\r\n");
    Serial_trans_String(" SPDD(P means PortIndex(0/1/2), DD means Data) to SET\r\n");
    Serial_trans_String(" GP(P means PortIndex(0/1/2)) to GET\r\n");
    Serial_trans_String(" X to reset buffer.\r\n");
    Serial_trans_String(" Serial:9600,8,none,1\r\n");
    Serial_trans_String("********************************\r\n");


    while (1)
    {
        recvProc();
    }
}


