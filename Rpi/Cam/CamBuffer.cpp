#include "CamBuffer.hpp"
#include "Assert.hpp"

namespace Rpi
{
    Rpi::CamBuffer::CamBuffer(U32 id_)
    : CamBuffer()
    {
        this->id = id_;
    }

    void CamBuffer::incref()
    {
        ref_count++;
    }

    void CamBuffer::decref()
    {
        FW_ASSERT(ref_count >= 1, ref_count);
        ref_count--;
    }

    bool CamBuffer::in_use() const
    {
        return ref_count > 0;
    }

    CamBuffer::CamBuffer()
    : id(0), ref_count(0)
    {
    }
}
