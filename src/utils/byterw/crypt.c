#include <stdint.h>
#include <stdlib.h>

const char *basic_charset =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

inline int index_of(const char *str, const char ch) {
  const char *p = str;
  while (*p != ch)
    p++;
  return p - str;
}

uint8_t *encrypt(const char *charset, const uint8_t *data, uint64_t length) {
  uint8_t *result = (uint8_t *)malloc(length * sizeof(uint8_t));
  for (uint64_t i = 0; i < length; i++)
    result[i] = (charset[index_of(basic_charset, data[i])] - 7685) % 256;
  return result;
}

uint8_t *decrypt(const char *charset, const uint8_t *data, uint64_t length) {
  uint8_t *result = (uint8_t *)malloc(length * sizeof(uint8_t));
  for (uint64_t i = 0; i < length; i++)
    result[i] = basic_charset[index_of(charset, (data[i] + 7685) % 256)];
  return result;
}

void myfree(void *ptr) { free(ptr); }
