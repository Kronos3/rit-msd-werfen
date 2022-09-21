
#ifndef WERFEN_DISPLAYIMPL_H
#define WERFEN_DISPLAYIMPL_H

#include <Rpi/Display/DisplayComponentAc.hpp>
#include "oled.hpp"
#include <Os/Mutex.hpp>

namespace Rpi
{
    class Display :
            public DisplayComponentBase,
            public Oled
    {
    public:
        explicit Display(const char* name);

        void init(NATIVE_INT_TYPE instance);

        void oled_init();

        void write(U32 line_number, const char* text);

    PRIVATE:

        void WRITE_cmdHandler(
                FwOpcodeType opCode,
                U32 cmdSeq,
                U8 lineIndex,
                const Fw::CmdStringArg &lineText
        ) override;

    PRIVATE:

        Os::Mutex m_access;

        void i2c_write(U8* data, U32 len) override;
    };
}

#endif //WERFEN_DISPLAYIMPL_H