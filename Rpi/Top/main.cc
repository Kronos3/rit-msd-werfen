//#include <cfg/vo_car.h>

#include <Logger.hpp>
#include <csignal>
#include "Components.hpp"

Kernel* kernel = nullptr;

static void sighandler(int signum)
{
    (void) signum;
    if (!kernel)
    {
        return;
    }

    Fw::Logger::logMsg("Exiting tasks\n");
    kernel->exit();
}

I32 main()
{
    kernel = new Kernel();

    // register signal handlers to exit program
    signal(SIGINT, sighandler);
    signal(SIGTERM, sighandler);

    Fw::Logger::logMsg("Booting up\n");

    kernel->start();

    // Run all functions until a shutdown is invoked
    kernel->run();

    Fw::Logger::logMsg("Shutting down\n");
    delete kernel;
    kernel = nullptr;

    return 0;
}
