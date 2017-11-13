51mcu receive Arduino UNO R3(run grbl)'s signal and control the 35BYJ46

only a few signals are accept by 51mcu:
x step			P1^0    up edge valid default
x direct		P1^1
y step			P1^2    up edge valid default
y direct		P1^3
step enable		P1^4    no used
splindle enable		P1^5

steper1_A	P2^0
steper1_B	P2^1
steper1_C	P2^2
steper1_D	P2^3
steper2_A	P2^4
steper2_B	P2^5
steper2_C	P2^6
steper2_D	P2^7

