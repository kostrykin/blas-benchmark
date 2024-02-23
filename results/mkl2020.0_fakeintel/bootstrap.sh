gcc -shared -fPIC -o "$1/libfakeintel.so" "$2/fakeintel.c"
export LD_PRELOAD="$1/libfakeintel.so"
