//#include <cfg/vo_car.h>

#include <Logger.hpp>
#include <csignal>

#include <Rpi/Top/RpiTopologyAc.hpp>

static void sighandler(int signum)
{
//    (void) signum;
//    if (!kernel)
//    {
//        return;
//    }
//
//    Fw::Logger::logMsg("Exiting tasks\n");
//    kernel->exit();
}

I32 main()
{
    // register signal handlers to exit program
    signal(SIGINT, sighandler);
    signal(SIGTERM, sighandler);

    Fw::Logger::logMsg("Booting up\n");

    Fw::Logger::logMsg("Shutting down\n");

    return 0;
}
