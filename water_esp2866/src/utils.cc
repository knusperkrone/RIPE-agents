#include "utils.h"

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

char *concat(char *buffer, int count, ...) {
    va_list arguments;
    char *bufferBase = buffer;

    va_start(arguments, count);
    for (int i = 0; i < count; i++) {
        const char *toAppend = va_arg(arguments, char *);
        size_t len = strlen(toAppend);
        memcpy(bufferBase, toAppend, len);
        bufferBase += len;
    }
    va_end(arguments);
    
    *bufferBase = '\0';
    return buffer;
}