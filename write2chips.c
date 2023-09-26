#include <stdint.h>
#include <stdbool.h>
#include "spi23x640/spi23x640.c"

uint16_t img_write2() {

    uint8_t csv_data[8192];
    FILE *file =fopen("WrittenImage.csv", "r");

    if (file == NULL) {
        perror("Error opening file");
        return 1;
    }

    // Discard the first line (header)
    char buffer[16];
    if (fgets(buffer, sizeof(buffer), file) == NULL) {
        perror("Error reading header");
        fclose(file);
        return 1;
    }

    for (int i = 0; i < 8192; i++) {
        if (fgets(buffer, sizeof(buffer), file) == NULL) {
            perror("Error reading data");
            fclose(file);
            return 1;
        }
        
        // Parse the "Address" and "Byte" data
        unsigned int address;
        unsigned int byte;
        if (sscanf(buffer, "%4x,%2x", &address, &byte) != 2) {
            perror("Error parsing data");
            fclose(file);
            return 1;
        }

        // Store the byte data in the array
        csv_data[i] = (uint8_t)byte;
    }

    fclose(file);

    spi23x640_init(5000000);
	uint16_t address_idx;
	for (address_idx = 0; address_idx <= SPI23X640_MAX_ADDRESS; address_idx++) {
		//printf("%x\n", address_idx);
		uint8_t next_value = csv_data[address_idx];
		spi23x640_write_byte(address_idx, next_value);

		//printf("Writing value %04" PRIx16 "\n", next_value);

	}	
    spi23x640_close();
    printf("Done Writing Image to Chip 1.");
    spi23x640_init2(5000000);
    for (address_idx = 0; address_idx <= SPI23X640_MAX_ADDRESS; address_idx++) {
		//printf("%x\n", address_idx);
		uint8_t next_value = csv_data[address_idx];
		spi23x640_write_byte(address_idx, next_value);

		//printf("Writing value %04" PRIx16 "\n", next_value);

	}	
    spi23x640_close2();
    printf("Done Writing Image to Chip 2.");
    return 0;
}

int main()
{
    if (img_write2() != 0)  {
        printf("Error: image not written.");
    }
}