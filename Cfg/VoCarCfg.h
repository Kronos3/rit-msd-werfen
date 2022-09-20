#ifndef WERFEN_VO_CAR_H
#define WERFEN_VO_CAR_H

enum
{
    CAMERA_LIBCAMERA_BUFFER_N = 8,           //!< Internal libcamera buffers
//    CAMERA_RAW_WIDTH = 1920,
//    CAMERA_RAW_HEIGHT = 1080,
    CAMERA_RAW_WIDTH = 1640,
    CAMERA_RAW_HEIGHT = 1232,
//    CAMERA_RAW_WIDTH = 640,
//    CAMERA_RAW_HEIGHT = 480,

    VIS_CHESSBOARD_DOWNSCALE = 2,            //!< Downscale factor during rough step of chessboard

    NAV_PID_HISTORY_N = 8,                   //!< Length of the PID history for integral
};

#endif //WERFEN_VO_CAR_H
