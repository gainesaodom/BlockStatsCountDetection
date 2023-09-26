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

#include "spi23x640/spi23x640.c"

#define FILE_NAME "test"

int main()
{

    FILE *file = fopen(FILE_NAME ".csv", "w");

    spi23x640_init(5000000);
	
    fprintf(file, "Address,Word");
    // SPI23X640_MAX_ADDRESS
    for (int i = 0; i <= SPI23X640_MAX_ADDRESS; i++)
    {
        uint8_t f = spi23x640_read_byte(i);
        fprintf(file, "%04" PRIx16 ",%02" PRIx8 "\n", i, f);
    }

    spi23x640_close();

    spi23x640_init2(5000000);
	
    // SPI23X640_MAX_ADDRESS
    for (int i = 0; i <= SPI23X640_MAX_ADDRESS; i++)
    {
        uint8_t f = spi23x640_read_byte(i);
        fprintf(file, "%04" PRIx16 ",%02" PRIx8 "\n", i, f);
    }

    spi23x640_close2();

    fclose(file);

    printf("Done reading both chips. Output file is %s.\n", FILE_NAME);
}
