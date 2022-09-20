
#include "DisplayImpl.h"
#include "Logger.hpp"

namespace Rpi
{
    DisplayImpl::DisplayImpl(const char* name)
    : DisplayComponentBase(name), Oled()
    {
    }

    void DisplayImpl::init(NATIVE_INT_TYPE instance)
    {
        DisplayComponentBase::init(instance);
    }

    void DisplayImpl::oled_init()
    {
        Oled::init();
    }

    void DisplayImpl::i2c_write(U8* data, U32 len)
    {
        Fw::Buffer i2c_buffer(data, len);
        Drv::I2cStatus status = i2c_out(0, I2C_ADDRESS, i2c_buffer);

        if (status != Drv::I2cStatus::I2C_OK)
        {
            Fw::Logger::logMsg("Failed to write i2c to display: %d\n",
                               status.e);
        }
    }

    void DisplayImpl::write(U32 line_number, const char* text)
    {
        FW_ASSERT(text);
        FW_ASSERT(line_number < 4, line_number);

        m_access.lock();

        line(line_number, 0, text);
        draw();

        m_access.unLock();
    }

    void DisplayImpl::WRITE_cmdHandler(U32 opCode, U32 cmdSeq, U32 line_number, const Fw::CmdStringArg &text)
    {
        write(line_number, text.toChar());
        cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse::OK);
    }
}
