#pragma once

#include <string.h>

#include <cstdarg>

char *iota(int val, char *buffer, unsigned int length);
char *concat(char *buffer, int count, ...);
