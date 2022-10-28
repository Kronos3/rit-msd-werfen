#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>

#include "libcvcam.h"

namespace Rpi
{
    struct CvCamImpl
    {
        cv::VideoCapture cam;
    };

    CvCam::CvCam(Rpi::Cam* cam)
    : m_cam(cam), m_impl(new CvCamImpl)
    {
    }

    CvCam::~CvCam()
    {
        delete m_impl;
    }

    void CvCam::open(I32 cameraId, CvCam::VideoCaptureAPIs api)
    {
        m_impl->cam.open(cameraId, api);
    }

    void CvCam::close()
    {
        if (m_impl->cam.isOpened())
        {
            m_impl->cam.release();
        }
    }
}
