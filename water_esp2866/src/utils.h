#pragma once

#include <string.h>
#include <cstdarg>

#define ARRAY_SIZE(ARRAY) (sizeof(ARRAY) / sizeof(ARRAY[0]))

char *iota(int val, char *buffer, unsigned int length);
char *concat(char *buffer, int count, ...);
