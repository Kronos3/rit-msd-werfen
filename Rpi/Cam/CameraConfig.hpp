#ifndef WERFEN_CAMERACONFIG_H
#define WERFEN_CAMERACONFIG_H

#include <Fw/Types/BasicTypes.hpp>

struct CameraConfig
{
    U32 frame_rate = 30;                                  //!< Frame-rate cap, 0 for none
    U32 exposure_time = 0;                                //!< Exposure time/shutter speed
    F32 gain = 10.0;                                      //!< Signal gain in dB
    F32 awb_gain_r = 0.0;                                 //!< Custom mode AWB red gain
    F32 awb_gain_b = 0.0;                                 //!< Custom mode AWB blue gain
    F32 brightness = 0.0;                                 //!< Brightness gain
    F32 contrast = 1.0;                                   //!< Contrast
    F32 saturation = 1.0;                                 //!< Color saturation
    F32 sharpness = 1.0;                                  //!< Sharpness
};

#endif //WERFEN_CAMERACONFIG_H
