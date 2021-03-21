/*
 * File:   ServoCont.c
 * Author: Michael
 * Program steuert Motor mit P-Regler via MotorEncoder an RA0 und PWM out an RB0
 * Bei WriteBefehl via I2c (1 = Encoder1 , 2 = Encoder  2) daten bereitstellen (Encoder ungleich 1 or 2 Error Wert senden)
 * Wenn ReadBefehl via I2c Encoder1 oder Enc.2 Pulse senden und Pulse auf Null setzen
 * Created 
 * STATUS: 
 */


#include <xc.h>
#include <pic16f88.h>


// #pragma config statements should precede project file includes.
// Use project enums instead of #define for ON and OFF.

// CONFIG
#pragma config FOSC = INTOSCIO   // INTRC oscillator; port I/O function on both RA6/OSC2/CLKO pin and RA7/OSC1/CLKI pin)
#pragma config WDTE = OFF       // Watchdog Timer Enable bit (WDT disabled)
#pragma config PWRTE = OFF      // Power-up Timer Enable bit (PWRT disabled)
#pragma config MCLRE = ON       // RA5/MCLR/VPP Pin Function Select bit (RA5/MCLR/VPP pin function is MCLR)
#pragma config BOREN = OFF      // Brown-out Reset Enable bit (BOR disabled)
#pragma config LVP = OFF        // Low-Voltage Programming Enable bit (RB3 is digital I/O, HV on MCLR must be used for programming)
#pragma config CPD = OFF        // Data EE Memory Code Protection bit (Code protection off)
#pragma config WRT = OFF        // Flash Program Memory Write Enable bits (Write protection off)
#pragma config CCPMX = RB3      // CCP1 Pin Selection bit (CCP1 function on RB0)
#pragma config CP = OFF         // Flash Program Memory Code Protection bit (Code protection off)
// CONFIG2
#pragma config FCMEN = OFF      // Fail-Safe Clock Monitor Enable bit (Fail-Safe Clock Monitor disabled)
#pragma config IESO = OFF       // Internal External Switchover bit (Internal External Switchover mode disabled)

//Ports 
#define EncoderA PORTBbits.RB0
#define EncoderB PORTBbits.RB2
#define current_LED PORTBbits.RB5
#define DirectionL PORTBbits.RB6
#define DirectionR PORTBbits.RB7
#define Debug_LED PORTAbits.RA0

// PWM Infos
#define _XTAL_FREQ 8000000
#define TMR2PRESCALE 4
#define PWM_freq 1000

char cDummy;
char data_arr[2] = {255, 255};
char data_index;
char timer_over;
signed int counting_pulse, actual_speed;
signed int enc_counts = 0;
signed int save_enc1;
signed int pwm_setting = 0;
signed int diff = 0;
char encoder_old;
int new1, diff1;
int last1;
int heating_up;


void __interrupt I2C()// In t e r r u p t r o u t i n e
{

    if (INTCONbits.INT0IF == 1) {
        if (EncoderB == 1) {
            enc_counts += 1;
        } else {
            enc_counts -= 1;
        }
        INTCONbits.INT0IF = 0;
        return;
    }
    if (INTCONbits.TMR0IF == 1) { //Timer Interrupt 
        INTCONbits.TMR0IF = 0; // Clear Flag
        INTCONbits.TMR0IE = 1;
        TMR0 = 200; // 100 -> 20ms @ 8Mhz
        timer_over = 1;
        return;
    }

    if (SSPSTATbits.R_nW == 0) {
        // Schreibzugriffe ( aus Sicht des Masters , d.h. Slave muss Daten aus dem Sende?
        // und Empfangsbuffer (SSPBUF) lesen )
        if (SSPSTATbits.D_nA == 0) {
            // State 1 : I2C write operation , last byte was an address byte
            // SSPSTAT bits : S=1, D/A=0, R/W=0, BF=1
            cDummy = SSPBUF;
            data_index = 0;
            SSPSTATbits.BF = 0; // Flag Buf f er?Ful l l oe s chen
            SSPCONbits.CKP = 1; // Cl o c k s t r e t ch i n g er lauben
            PIR1bits.SSPIF = 0; // SSP?Int e r rupt?Flag wi eder l oe s chen
            return;
        } else {
            // State 2 : I2C write operation , last byte was a data byte
            // SSPSTAT bits : S=1, D/A=1, R/W=1, BF=1
            data_arr[data_index] = SSPBUF; //Data lesen und sichern // Datenbyte von SSPBUF lesen und am
            data_index += 1;
            
            SSPCONbits.CKP = 1; // Cl o c k s t r e t ch i n g er lauben
            PIR1bits. SSPIF = 0; // SSP? Interrupt?Flag wieder loeschen
            return;
        }
    } else {
        // Lesezugriff ( aus Sicht des Masters , d.H. Slave muss Daten in Sende und
        // Empfangsbuffer (SSPBUF) schreiben )
        if (SSPSTATbits.D_nA == 0) {
        data_index = 0;
        switch (data_arr[0])
        {
        case 0:
              SSPBUF = 11;
        case 1:
            SSPBUF = enc_counts;               
            break;
        default:                        
            SSPBUF = 3;
            break;      
        }
        SSPCONbits.CKP = 1 ;            // Clockstretchinger erlauben
        PIR1bits.SSPIF = 0 ;            // SSP?Interrupt?Flagwieder loeschen
        return;
    } else {
            // State 4 : I2C read operation , last byte was a data byte
            // SSPSTAT bits : S=1, D/A=1, R/W=0, BF=0
            SSPBUF = cDummy;
            SSPCONbits.CKP = 1; // Cl o c k s t r e t ch i n g er lauben
            PIR1bits.SSPIF = 0; // SSP?Int e r rupt?Flag wi eder l oe s chen
            return;
        }
    }
}

void I2C_Slave_Init(short address) {
    SSPSTAT = 0;
    SSPADD = address;
    SSPCON = 0x36;
    TRISBbits.TRISB1 = 1; //Setting as input as given in datasheet
    TRISBbits.TRISB4 = 1; //Setting as input as given in datasheet
    GIE = 1;
    PEIE = 1;
    SSPIF = 0;
    SSPIE = 1;
}

void init_Int_change(void) {
    TRISBbits.TRISB0 = 1; // Pin0 Input
    OPTION_REGbits.INTEDG = 1; // Rising edge INT change =1
    INTCONbits.INT0IF = 0; // clear INT flag     
    INTCONbits.INT0IE = 1; // Interuppt for INT Change ON=1
    INTCONbits.GIE = 1; // Global Int. ON
}

void port_init(void) {
    OSCCON = 0b01110000; //Interner Osci 8Mhz
    nRBPU = 0; //Enables PORTB internal pull up resistors
    ANSEL = 0x00; // A/D off = 0
    
    TRISB = 0x00; //PORTB ALL Out
    TRISBbits.TRISB0 = 1;
    TRISBbits.TRISB2 = 1;
    PORTB = 0x00; //All PortB OFF
    
    TRISA = 0xFF; //PORTA ALL In
    TRISAbits.TRISA0 = 0; //PA0 Out
    
}

void init_timer0(void) {
    OPTION_REGbits.T0CS = 0; //Internal Count
    OPTION_REGbits.PSA = 0; //Prescaler to Timer0
    OPTION_REGbits.PS2 = 0; //Prescaler
    OPTION_REGbits.PS1 = 0; //Prescaler
    OPTION_REGbits.PS0 = 0; //Prescaler
    TMR0 = 200; // 100 -> 20ms @ 8Mhz
    INTCONbits.TMR0IF = 0; // Clear Flag
    //INTCONbits.TMR0IE = 1; //Interuppt ON
    //INTCONbits.GIE = 1; // Global INt. ON
}

void p_regler(void) {
    diff = data_arr[1] - actual_speed; // Soll - ist
    diff = diff * -2; //P-Wert normaly 2-10

    pwm_setting = pwm_setting + diff;

    if (data_arr[1] == 255) { //Stop PWM
        pwm_setting = 0;
    }

    if (pwm_setting <= 0) { //Prevent wind-up
        pwm_setting = 0;
    }
    if (pwm_setting >= 1023) {
        pwm_setting = 1023;
    }
}

void direction(void) {

    if (data_arr[0] == 128) {
        DirectionL = 0;
        DirectionR = 1;
    } else {
        DirectionL = 1;
        DirectionR = 0;
    }
}

void init_pwm(void) {
    PR2 = (_XTAL_FREQ / (PWM_freq * 4 * TMR2PRESCALE)) - 1; //Setting the PR2 formulae using Datasheet // Makes the PWM work in ?2KHZ?
    CCP1M3 = 1;
    CCP1M2 = 1; //Configure the CCP1 module CCP1M3 and CCP1M2 = 1 sets PWM 
    T2CKPS0 = 1;
    T2CKPS1 = 0; //Timer2 presacler to 01 = 4 
    TMR2ON = 1; //Configure the Timer module
    TRISBbits.TRISB3 = 0; // make portB/3 output (ConfigBit muss config CCPMX = RB3 starr RB0)
}

void init_comparator(void) {
    CMCONbits.CM0 = 1; //Comparator Mode
    CMCONbits.CM1 = 0;
    CMCONbits.CM2 = 1;
    CMCONbits.C1INV = 0; //Comp-1 invert if 1
    CMCONbits.C2INV = 0; //Comp-2 invert if 1
    ANSELbits.ANS1 = 1; // 1 make analog In
    ANSELbits.ANS2 = 1; // 1 make analog In  
    TRISAbits.TRISA1 = 1;
    TRISAbits.TRISA2 = 1;
}

over_current(void) {
    if (CMCONbits.C2OUT == 1) {
        heating_up += 1;
        current_LED = 1;
    } else {
        heating_up -= 1;
        current_LED = 0;
    }

    if (heating_up > 50) {  //Limit Current after ca. 1sec
        pwm_setting = 900;
    }

    if (heating_up > 400) {  //Limit Current after ca. 8sec
        pwm_setting = 50;
    }
    
    if (heating_up < 1) {
        heating_up = 1;
    }
    if (heating_up > 1000) {
        heating_up = 1000;
    }
}

pwm_duty(unsigned int duty) {
    if (duty <= 1023) {
        //duty = ((float) duty / 1023)*(_XTAL_FREQ / (PWM_freq * TMR2PRESCALE)); // On reducing //duty = (((float)duty/1023)*(1/PWM_freq)) / ((1/_XTAL_FREQ) * TMR2PRESCALE);
        CCP1X = duty & 1; //Store the 1st bit
        CCP1Y = duty & 2; //Store the 0th bit
        CCPR1L = duty >> 2; // Store the remining 8 bit
    }
}

void main() {
    port_init();
    Debug_LED = 1;
    
    //I2C_Slave_Init(0x32); // Motor #1 = 19 on RasPi Initialize as a I2C Slave with address 0x32
    //I2C_Slave_Init(0x34); // Motor #2
    //I2C_Slave_Init(0x36); // Motor #3
    I2C_Slave_Init(0x38); // Motor #4
    //init_timer0();
    pwm_duty(0);
    init_pwm();
    init_comparator();
    init_Int_change();
    
    while (1) {

        counting_pulse += 1;
        if (counting_pulse >= 1023) {
            counting_pulse = 1023;
        }
        if ((EncoderA != encoder_old) || (counting_pulse == 1023)) {
            actual_speed = counting_pulse;
            counting_pulse = 0;
            encoder_old = EncoderA;

            p_regler();
            
            direction();

            over_current();

            pwm_duty(pwm_setting);
        }
        Debug_LED = 0;
    }
}
