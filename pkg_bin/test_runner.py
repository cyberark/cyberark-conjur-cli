import ssl
print(ssl.OPENSSL_VERSION)
ssl.FIPS_mode_set(0)
print(ssl.FIPS_mode())