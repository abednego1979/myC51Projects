51mcu receive Arduino UNO R3(run grbl)'s signal and control the 35BYJ46




only a few signals are accept by 51mcu:
x step			P0^0    up edge valid default
x direct		P0^1
y step			P0^2    up edge valid default
y direct		P0^3
z step			P0^4    up edge valid default
z direct		P0^5
step enable		P0^6

output signals:
steperx_A	P1^0
steperx_B	P1^1
steperx_C	P1^2
steperx_D	P1^3
stepery_A	P1^4
stepery_B	P1^5
stepery_C	P1^6
stepery_D	P1^7

steperz_A	P2^0
steperz_B	P2^1
steperz_C	P2^2
steperz_D	P2^3

