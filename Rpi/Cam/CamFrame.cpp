//
// Created by tumbar on 9/21/22.
//

#include <Rpi/Cam/CamFrame.hpp>

namespace Rpi
{
    CamFrame::CamFrame()
    : m_mat(nullptr)
    {
    }

    CamFrame::CamFrame(cv::Mat* m)
    : m_mat(m)
    {
    }

    cv::Mat* CamFrame::get() const
    {
        return m_mat;
    }

    Fw::SerializeStatus CamFrame::deserialize(Fw::SerializeBufferBase &buffer)
    {
        POINTER_CAST m;
        auto stat = buffer.deserialize(m);

        m_mat = reinterpret_cast<cv::Mat*>(m);
        return stat;
    }

    Fw::SerializeStatus CamFrame::serialize(Fw::SerializeBufferBase &buffer) const
    {
        auto m = reinterpret_cast<POINTER_CAST>(m_mat);
        return buffer.serialize(m);
    }
}
