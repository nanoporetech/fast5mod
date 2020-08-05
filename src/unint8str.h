#ifndef _UINT8STR_H
#define _UINT8STR_H

#include <stdint.h>

/** Format a uint32_t to a string
 *
 * @param value to format.
 * @param dst destination char.
 * @returns length of string.
 *
 */
size_t uint8_to_str(uint8_t value, char *dst);

/** Format an array values as a comma seperate string
 *
 * @param values integer input array
 * @param length size of input array
 * @param result output char buffer of size 4 * length * sizeof char
 * @returns void
 *
 * The output buffer size comes from:
 *    a single value is max 3 chars
 *    + 1 for comma (or \0 at end)
 */
void format_uint8_array(uint8_t* values, size_t length, char* result);

#endif
