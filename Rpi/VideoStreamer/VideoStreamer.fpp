module Rpi {

    active component VideoStreamer {

        # -----------------------------
        # General ports
        # -----------------------------

        output port incref: Frame
        output port decref: Frame
        output port frameGet: FrameGet

        @ Output frames
        async input port frame: Frame

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
        # Commands
        # -----------------------------

        @ Stream video over UDP connection
        async command OPEN()

        enum DisplayLocation {
            NONE @< Dump the frames immediately
            HDMI @< Display video stream over on-board HDMI port
            UDP @< Stream video over UDP to HOSTNAME:PORT
            BOTH @< Stream to both UDP and HDMI simultaneously
        }

        @ Start camera stream
        async command DISPLAY(
            where: DisplayLocation @< Where to display frames
            )

        # -----------------------------
        # Events
        # -----------------------------

        event StreamingTo(where: DisplayLocation) \
            severity activity low \
            format "Now streaming to {}"

        event InvalidFrameBuffer(frameId: U32) \
            severity warning low \
            format "Received an invalid frame id {}"

        @ Hostname to stream UDP packets to
        param HOSTNAME: string size 32

        @ Port to stream UDP packets to
        param PORT: U16 default 8000

        @ Frame output rate
        telemetry FramesPerSecond: U32 format "{} fps"

        @ Total number of frames sent to the video streamer
        telemetry FramesTotal: U32

        @ Number of UDP packets sent to server
        telemetry PacketsSent: U32
    }

}