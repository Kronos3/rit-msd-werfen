module Rpi {

    type CamFrame

    port Frame(frameId: U32)
    port FrameGet(frameId: U32, ref frame: CamFrame) -> bool

    port CamSignal()

    active component Cam {

        # -----------------------------
        # General ports
        # -----------------------------

        @ Increment reference count on frame
        sync input port incref: Frame

        @ Decrement reference count on frame
        async input port decref: Frame

        @ Output frames
        output port frame: Frame

        @ Get frame data
        sync input port frameGet: FrameGet

        async input port start: CamSignal
        async input port stop: CamSignal

        async input port capture: CamSignal

        # -----------------------------
        # Special ports
        # -----------------------------

        @ Command receive port
        command recv port CmdDisp

        @ Command registration port
        command reg port CmdReg

        @ Command response port
        command resp port CmdStatus

        @ Event port
        event port Log

        @ Text event port
        text event port LogText

        @ Time get port
        time get port Time

        @ Telemetry port
        telemetry port Tlm

        @ A port for getting parameter values
        param get port ParamGet

        @ A port for setting parameter values
        param set port ParamSet

        # -----------------------------
        # Events
        # -----------------------------

        event CameraManagerStartFailed(errCode: I32) \
            severity warning high \
            format "Camera Manager failed to start, code {}"

        event NoCameras() \
            severity warning high \
            format "No cameras available"

        event CameraOutOfRange(camId: U32, numCameras: U32) \
            severity warning high \
            format "Requested camera {} is out of range, only {} cameras available"

        event CameraName(camId: U32, camName: string size 64) \
            severity diagnostic \
            format "Found camera at index {} with name {}"

        event CameraFindFailed(camName: string size 64) \
            severity warning high \
            format "Failed to map camera name {} back to camera via camera manager"

        event CameraAcquireFailed(camName: string size 64) \
            severity warning high \
            format "Failed to acquire camera lock on {}"

        event CameraOpened(camName: string size 64) \
            severity activity low \
            format "Successfully opened camera {}"

        event CameraConfigInitFailed(camName: string size 64) \
            severity warning high \
            format "Failed to initialize camera configuration for {}"

        enum ConfigurationValidity {
            VALID
            ADJUSTED
            INVALID
        }

        event CameraConfigValidation(camName: string size 64,
                                     validity: ConfigurationValidity) \
            severity diagnostic \
            format "Camera {} configuration is {}"

        event CameraConfigFailed(camName: string size 64,
                                 errCode: I32) \
            severity warning high \
            format "Camera {} failed to configure, core {}"

        event CaptureFailed() \
            severity warning low \
            format "Camera capture failed, dropping frame"

        event ImageSaving(destination: string size 80) \
            severity activity low \
            format "Saving image to file {}"

        event CameraStarting() \
            severity activity low \
            format "Camera is starting"

        event CameraStopping() \
            severity activity low \
            format "Camera is stopping"

        event CameraBusy() \
            severity warning low \
            format "Camera is already streaming"

        event CameraNoListener(frameId: U32) \
            severity warning low \
            format "Got frame with ID {} from camera without an active listener"

        event CameraConfiguring() \
            severity activity low \
            format "Sending configuration to camera"

        event CameraInvalidGet(bufId: U32) \
            severity warning low \
            format "Attempting to get frame buffer with ID not in use {}"

        event CameraInvalidIncref(bufId: U32) \
            severity warning low \
            format "Attempting to incref on buffer with ID not in use {}"

        event CameraInvalidDecref(bufId: U32) \
            severity warning low \
            format "Attempting to decref on buffer with ID not in use {}"

        @ Camera frame rate
        param FRAME_RATE: U32 default 30

        @ Exposure time, 0 for hardware minimum
        param EXPOSURE_TIME: U32 default 0

        @ Sensor gain, dB
        param GAIN: F32 default 10.0

        @ Auto white balance red gain, dB
        param AWB_GAIN_R: F32 default 0.0

        @ Auto white balance blue gain, dB
        param AWB_GAIN_B: F32 default 0.0

        @ Brightness
        param BRIGHTNESS: F32 default 0.0

        @ Contrast
        param CONTRAST: F32 default 1.0

        @ Saturation, 1 for color, 0 for bw
        param SATURATION: F32 default 1.0

        @ Sharpness
        param SHARPNESS: F32 default 1.0

        telemetry FramesCapture: U32 update on change \
            format "{} frames captured"

        telemetry FramesDropped: U32 update on change \
            format "{} frames dropped"

        telemetry FramesFailed: U32 update on change \
            format "{} frames failed to capture"
    }

}