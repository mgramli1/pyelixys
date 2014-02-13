
#ifndef PYLINACT_H
#define PYLINACT_H

#include <linactbuf.h>
#include <linact.hpp>

#ifdef BUILD_DLL
// Export DLL
#define EXPORT_DLL __declspec(dllexport)
#else
#define EXPORT_DLL __declspec(dllimport)
#endif

using namespace IAI;

extern "C" {


LinActBuf* LinActBuf_new();

}

#endif
