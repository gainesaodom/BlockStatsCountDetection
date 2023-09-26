/*
SPI API for the 23K640 SRAM chip
*/

#include <stdio.h>
#include <errno.h>
#include <stdint.h>
#include <linux/spi/spidev.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <string.h>
#include <inttypes.h>
#include <wiringPi.h>

#include "spi23x640/spi23x640.c"

#define FGEN_PIN 0
char date [100];
char file_name [116];
volatile int s=1;

void chip_on(void)
{
    
    if (s <= 100) {
        printf("Starting %d... ", s);

        snprintf(file_name, sizeof(file_name), "%s_%d.csv", date, s);
        FILE *file = fopen(file_name, "w");  

        fprintf(file,"Address,Word\n");

        // SPI23X640_MAX_ADDRESS
            for (int i = 0; i <= SPI23X640_MAX_ADDRESS; i++)
            {
                uint8_t f = spi23x640_read_byte(i);
                fprintf(file, "%04" PRIx16 ",%02" PRIx8 "\n", i, f);
            }
        fclose(file);
        printf("Done!\n");
    }
    else 
    {
    printf("Completely Done!\n");
}
s++;
}


int main()
{
    printf("What is today's date? (Use format JUL4 for July 4th): ");
    scanf("%99s", date);
    mkdir(date, 0777);
    chdir(date);
    spi23x640_init(5000000);

    if (wiringPiSetup() == -1) {
        printf("WiringPi initialization failed.\n");
        return 1;
    }

    pinMode(FGEN_PIN, INPUT);

    // Set up the interrupt handler
    if (wiringPiISR(FGEN_PIN, INT_EDGE_RISING, &chip_on) < 0) {
        printf("Unable to set up ISR.\n");
        return 1;
    }

    pullUpDnControl(FGEN_PIN, PUD_DOWN);

    while(s <= 101)
    {
        
    }

    spi23x640_close();

    // printf("done\n");
}
