/*
SPI API for the 23K640 SRAM chip

supports reading and writing in "Byte Operation"
does not support reading status register
does not support "Page Operation" or "Sequential Operation"
does not support writing to status register
Author: Amaar Ebrahim
Email: aae0008@auburn.edu

HEY - IF YOU GET "Could not write SPI mode, ret = -1" THEN MAKE SURE YOU RUN
IT AS sudo <executable-path>
For example:
	sudo ./a.out
*/

#include <stdio.h>
#include <errno.h>
#include <stdint.h>
#include <linux/spi/spidev.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <string.h>
#include <assert.h>
#include <sys/stat.h>
#include <fcntl.h>

//#include "sram_print.c"

// constants that shouldn't be changed
#define SPI23X640_READ_CMD 0x03 // the command to read the SRAM chip is 0000_0011
#define SPI23X640_WRITE_CMD 0x02 // the command to write to the SRAM chip is 0000_0010
#define SPI23X640_RDSR_CMD 0x05 // the command to read the status register
#define SPI23X640_DEVICE "/dev/spidev0.0" // we're going to open SPI on bus 0 device 0
#define SPI23X640_DEVICE1 "/dev/spidev0.1" // we're going to open SPI on bus 0 device 1
#define SPI23X640_NUMBER_OF_BITS 8
#define SPI23X640_MAX_SPEED_HZ 20000000 // see datasheet
#define SPI23X640_DELAY_US 0 // delay in microseconds
#define SPI23X640_MAX_ADDRESS 8191

typedef struct spi_ioc_transfer spi_ioc_transfer;

// module properties
uint32_t mode;
uint32_t fd;
uint32_t fd2;
uint64_t spi23x640_speed_hz;
spi_ioc_transfer read_transfer;
spi_ioc_transfer write_transfer;

/*
    Useful for debugging
    Prints out the transfer and receive buffers of an ioctl transfer
*/
void print_tx_and_rx(uint8_t * tx, uint8_t * rx, uint16_t size) {
	int i;
        for (i = 0; i < size; i++) {
                printf("Index: %d \tTX: %d \tRX: %d\n", i, tx[i], rx[i]);
        }
}

/*
    Handles ioctl error messages in the read and write functions.
    I don't know why I'm not using this for errors that occur in the
    init function. Maybe I'll use this function to handle them later.
*/
void handle_message_response(int ret) {
    if (ret <= 0) {
		char buffer[256];
		strerror_r(errno, buffer, 256);
		printf("Error! SPI failed\t %s\n", buffer);
    }
}

/*
    Initialize the spi23x640 module
    Pass in a speed in HZ, which cannot be above SPI23X640_MAX_SPEED_HZ
*/
void spi23x640_init(uint64_t speed) {

    assert(speed < SPI23X640_MAX_SPEED_HZ);

    spi23x640_speed_hz = speed;

	// open device
    fd = open(SPI23X640_DEVICE, O_RDWR);
	if (fd < 0) {
		printf("Could not open\n");
		exit(EXIT_FAILURE);
	}


	// assign the mode - Mode 0 means (1) data is shifted in on the Rising
	// edge and shifted out on the falling edge, in accordance with
	// the SRAM device description, and (2) clock polarity is low in the idle state
	mode |= SPI_MODE_0;

	int ret = ioctl(fd, SPI_IOC_WR_MODE32, &mode);
	if (ret != 0) {
		printf("Could not write SPI mode, ret = %d\n", ret);
		close(fd);
		exit(EXIT_FAILURE);
	}

	
	// for SPI_MODE_n, the value of "mode" becomes n + 4 for whatever
	// reason after the line below. A forum post says this didn't
	// appear to be an issue for them
	ret = ioctl(fd, SPI_IOC_RD_MODE32, &mode);
	if (ret != 0) {
		printf("Could not read mode\n");
		close(fd);
		exit(EXIT_FAILURE);
	}

	// spi_speed_hz needs to be declared so a pointer can be passed to the calls to ioctl(). ioctl() won't accept constants because constants don't have pointers.
	//uint32_t spi_speed_hz = SPI_SPEED_HZ;
	// assign the speed of ioctl
	ret = ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &spi23x640_speed_hz);
	if (ret != 0) {
		printf("Could not write the SPI max speed...\r\n");
		close(fd);
		exit(EXIT_FAILURE);
	}
	
	ret = ioctl(fd, SPI_IOC_RD_MAX_SPEED_HZ, &spi23x640_speed_hz);
	if (ret != 0) {
		printf("Could not read the SPI max speed...\r\n");
		close(fd);
		exit(EXIT_FAILURE);
	}

	
}

/*
    Initialize the spi23x640 module
    Pass in a speed in HZ, which cannot be above SPI23X640_MAX_SPEED_HZ
*/
void spi23x640_init2(uint64_t speed) {

    assert(speed < SPI23X640_MAX_SPEED_HZ);

    spi23x640_speed_hz = speed;

	// open device
    fd2 = open(SPI23X640_DEVICE1, O_RDWR);
	if (fd2 < 0) {
		printf("Could not open\n");
		exit(EXIT_FAILURE);
	}


	// assign the mode - Mode 0 means (1) data is shifted in on the Rising
	// edge and shifted out on the falling edge, in accordance with
	// the SRAM device description, and (2) clock polarity is low in the idle state
	mode |= SPI_MODE_0;

	int ret = ioctl(fd2, SPI_IOC_WR_MODE32, &mode);
	if (ret != 0) {
		printf("Could not write SPI mode, ret = %d\n", ret);
		close(fd2);
		exit(EXIT_FAILURE);
	}

	
	// for SPI_MODE_n, the value of "mode" becomes n + 4 for whatever
	// reason after the line below. A forum post says this didn't
	// appear to be an issue for them
	ret = ioctl(fd2, SPI_IOC_RD_MODE32, &mode);
	if (ret != 0) {
		printf("Could not read mode\n");
		close(fd2);
		exit(EXIT_FAILURE);
	}

	// spi_speed_hz needs to be declared so a pointer can be passed to the calls to ioctl(). ioctl() won't accept constants because constants don't have pointers.
	//uint32_t spi_speed_hz = SPI_SPEED_HZ;
	// assign the speed of ioctl
	ret = ioctl(fd2, SPI_IOC_WR_MAX_SPEED_HZ, &spi23x640_speed_hz);
	if (ret != 0) {
		printf("Could not write the SPI max speed...\r\n");
		close(fd2);
		exit(EXIT_FAILURE);
	}
	
	ret = ioctl(fd2, SPI_IOC_RD_MAX_SPEED_HZ, &spi23x640_speed_hz);
	if (ret != 0) {
		printf("Could not read the SPI max speed...\r\n");
		close(fd2);
		exit(EXIT_FAILURE);
	}

	
}


/*
    Closes the spi connection. Use this once you're done with SPI.
*/
void spi23x640_close() {
    close(fd);
}

/*
    Closes the spi connection. Use this once you're done with SPI.
*/
void spi23x640_close2() {
    close(fd2);
}

/*
	Reads the status register of the chip
*/
uint8_t spi23x640_read_status_reg() {
	// initialize transmission and receive buffers
	uint8_t tx_buffer[2];
	uint8_t rx_buffer[2];
	int i;
	for (i = 0; i < 2; i++) {
		tx_buffer[i] = 0x00;
		rx_buffer[i] = 0xFF;
	}

	// populate transmission buffer with the (1) SRAM command, (2) address (split among 2 bytes)
    tx_buffer[0] = SPI23X640_RDSR_CMD;

	// configure transmission
    read_transfer.tx_buf = (unsigned long) tx_buffer;
    read_transfer.rx_buf = (unsigned long) rx_buffer;
    read_transfer.bits_per_word = SPI23X640_NUMBER_OF_BITS;
    read_transfer.speed_hz = spi23x640_speed_hz;
    read_transfer.delay_usecs = SPI23X640_DELAY_US;
    read_transfer.len = 2;

	// send transmission
	int ret = ioctl(fd, SPI_IOC_MESSAGE(1), &read_transfer);
	
	// print if there's an error needed
    handle_message_response(ret);
        
	//print_tx_and_rx(&tx_buffer, &rx_buffer, 4);

	// the byte at the address is expected in rx_buffer[3]
	return rx_buffer[1];
}




/*
    Write a single byte to a 16-bit address
*/
void spi23x640_write_byte(uint16_t addr, uint8_t data) {


	uint8_t tx_buffer[4] = {
		SPI23X640_WRITE_CMD,		// write command
		(uint8_t) (addr >> 8),	// upper 8 bits of the address
		(uint8_t) (addr & 0xFF),	// lower 8 bits of the address
	       	data			// data byte
	};		

	uint8_t rx_buffer[4] = {0xFF, 0xFF, 0xFF, 0xFF};
	


	write_transfer.tx_buf = (unsigned long) tx_buffer;
        write_transfer.rx_buf = (unsigned long) rx_buffer;
        write_transfer.bits_per_word = SPI23X640_NUMBER_OF_BITS;
        write_transfer.speed_hz = spi23x640_speed_hz;
        write_transfer.delay_usecs = SPI23X640_DELAY_US;
        write_transfer.len = 4;

	uint32_t ret = ioctl(fd, SPI_IOC_MESSAGE(1), &write_transfer);
    handle_message_response(ret);

	//print_tx_and_rx(&tx_buffer, &rx_buffer, 32);
}


/*
    Read a single byte at a 16-bit address
*/
uint8_t spi23x640_read_byte(uint16_t addr) {
	
	// initialize transmission and receive buffers
	uint8_t tx_buffer[4];
	uint8_t rx_buffer[4];
	int i;
	for (i = 0; i < 4; i++) {
		tx_buffer[i] = 0x00;
		rx_buffer[i] = 0xFF;
	}

	// populate transmission buffer with the (1) SRAM command, (2) address (split among 2 bytes)
    tx_buffer[0] = SPI23X640_READ_CMD;
    tx_buffer[1] = (uint8_t) (addr >> 8); // upper half of address
    tx_buffer[2] = (uint8_t) (addr & 0xFF); // lower half of address


	// configure transmission
    read_transfer.tx_buf = (unsigned long) tx_buffer;
    read_transfer.rx_buf = (unsigned long) rx_buffer;
    read_transfer.bits_per_word = SPI23X640_NUMBER_OF_BITS;
    read_transfer.speed_hz = spi23x640_speed_hz;
    read_transfer.delay_usecs = SPI23X640_DELAY_US;
    read_transfer.len = 4;

	// send transmission
	int ret = ioctl(fd, SPI_IOC_MESSAGE(1), &read_transfer);
	
	// print if there's an error needed
    handle_message_response(ret);
        
	//print_tx_and_rx(&tx_buffer, &rx_buffer, 4);

	// the byte at the address is expected in rx_buffer[3]
	return rx_buffer[3];
 


}