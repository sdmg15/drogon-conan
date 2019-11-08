#include "drogon/HttpAppFramework.h"

auto main() -> int {
    //Set HTTP listener address and port
    drogon::app().addListener("0.0.0.0",8080);
    //Load config file
    //drogon::app().loadConfigFile("../config.json");
    //Run HTTP framework,the method will block in the internal event loop
    drogon::app().run();
    return 0;
}