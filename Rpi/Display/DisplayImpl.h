
#ifndef WERFEN_DISPLAYIMPL_H
#define WERFEN_DISPLAYIMPL_H

#include <Rpi/Display/DisplayComponentAc.hpp>
#include "oled.h"
#include <Os/Mutex.hpp>

namespace Rpi
{
    class DisplayImpl :
            public DisplayComponentBase,
            public Oled
    {
    public:
        explicit DisplayImpl(const char* name);

        void init(NATIVE_INT_TYPE instance);
        void oled_init();

        void write(U32 line_number, const char* text);

    PRIVATE:
        void WRITE_cmdHandler(U32 opCode, U32 cmdSeq, U32 line_number, const Fw::CmdStringArg &text) override;

    PRIVATE:

        Os::Mutex m_access;

        void i2c_write(U8* data, U32 len) override;
    };
}

#endif //WERFEN_DISPLAYIMPL_H
