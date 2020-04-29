#include "utils.h"

#include <Arduino.h>

char *iota(int val, char *buffer, unsigned int length) {
    unsigned int i = 0;
    while (val != 0 && i < length - 1) {
        buffer[i++] = '0' + (val % 10);
        val /= 10;
    }

    buffer[i] = '\0';

    // reverse
    for (int low = 0, high = i - 1; low < high; low++, high--) {
        char temp = buffer[low];
        buffer[low] = buffer[high];
        buffer[high] = temp;
    }
    return buffer;
}

char *concat(char *buffer, const char *prefix, const char *suffix) {
    char *bufferBase = buffer;
    memccpy(bufferBase, prefix, '\0', strlen(prefix));
    bufferBase += strlen(prefix);
    memccpy(bufferBase, suffix, '\0', strlen(suffix));
    bufferBase += strlen(suffix);
    *bufferBase = '\0';
    return buffer;
}