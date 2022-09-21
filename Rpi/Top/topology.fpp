module Rpi {

    enum Port_RateGroups {
        rg1Hz
    }

    topology Rpi {
        # Core components
        instance systemTime
        instance eventLogger
        instance cmdDisp
        instance chanTlm
        instance prmDb
        instance fileManager
        instance cmdSeq
        # instance cmdSeq2

        # Rate groups
        instance blockDrv
        instance rgDriver
        instance rg1Hz

        # Rpi components
        instance cam
        instance framePipe
        instance display
        instance videoStreamer

        # ---------------------------------
        # Pattern graph connections
        # ---------------------------------

        command connections instance cmdDisp
        event connections instance eventLogger
        time connections instance systemTime

        param connections instance prmDb
        telemetry connections instance chanTlm

        # ---------------------------------
        # Core graph connections
        # ---------------------------------

        connections RateGroups {
            blockDrv.CycleOut -> rgDriver.CycleIn

            # Rate group 1Hz
            rgDriver.CycleOut[Port_RateGroups.rg1Hz] -> rg1Hz.CycleIn
            rg1Hz.RateGroupMemberOut[0] -> cmdSeq.schedIn
            rg1Hz.RateGroupMemberOut[1] -> chanTlm.Run
            # rg1Hz.RateGroupMemberOut[1] -> cmdSeq2.schedIn
            # rg1Hz.RateGroupMemberOut[2] -> cmdSeq2.schedIn

        }
    }

}