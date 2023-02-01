//
// Created by tumbar on 1/23/23.
//

#include <stddef.h>
#include "crc.h"

#define CRC_POLY_16 0xA001
#define CRC_START_16 0x0000

static U8 crc_tab16_init = 0;
static U16 crc_tab16[256];

static void init_crc16_tab(void)
{
    U16 i;
    U16 j;
    U16 crc;
    U16 c;

    for (i = 0; i < 256; i++)
    {
        crc = 0;
        c = i;

        for (j = 0; j < 8; j++)
        {
            if ((crc ^ c) & 0x0001) crc = (crc >> 1) ^ CRC_POLY_16;
            else crc = crc >> 1;

            c = c >> 1;
        }

        crc_tab16[i] = crc;
    }

    crc_tab16_init = 1;

}

U16 crc16(const U8* bytes, U32 n)
{
    if (!crc_tab16_init)
    {
        init_crc16_tab();
    }

    U16 crc;
    const U8* ptr;
    U32 a;

    crc = CRC_START_16;
    ptr = bytes;

    if (ptr != NULL)
    {
        for (a = 0; a < n; a++)
        {
            crc = (crc >> 8) ^ crc_tab16[(crc ^ (U16) * ptr++) & 0x00FF];
        }
    }

    return crc;
}
