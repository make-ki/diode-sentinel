"""Import-time fix so `import lightgbm` works on NixOS.

LightGBM is a C++ wheel: importing it dlopen()s lib_lightgbm.so, which
NEEDs libstdc++.so.6, libgomp.so.1 and libz.so.1 by SONAME. On an FHS
distro those always resolve. On NixOS they live in the store and are only
found if LD_LIBRARY_PATH points at them -- and, worse, *some* resolve via
ld.so.cache while others don't, so a single "is this NixOS?" probe is not
enough. We therefore try each SONAME, and on failure locate it under
/nix/store and preload it via ctypes with RTLD_GLOBAL. Once preloaded, the
dynamic linker satisfies later SONAME lookups from the already-loaded set.

Idempotent; a no-op on normal Linux/macOS.
"""
import ctypes
import glob
import sys

# store-path patterns per SONAME; the hash-prefixed directory names sort
# arbitrarily, so we just take whichever entry actually loads
_STORE_PATTERNS = {
    "libstdc++.so.6": ("/nix/store/*gcc-*/lib/libstdc++.so.6",
                       "/run/current-system/sw/lib/libstdc++.so.6"),
    "libgomp.so.1": ("/nix/store/*gcc-*/lib/libgomp.so.1",
                     "/nix/store/*gomp*/lib/libgomp.so.1",
                     "/run/current-system/sw/lib/libgomp.so.1"),
    "libz.so.1": ("/nix/store/*zlib-*/lib/libz.so.1",
                  "/run/current-system/sw/lib/libz.so.1"),
}


def _preload_from_store(soname):
    for pat in _STORE_PATTERNS.get(soname, ()):
        for path in glob.glob(pat):          # any match that loads is fine
            try:
                ctypes.CDLL(path, mode=ctypes.RTLD_GLOBAL)
                return True
            except OSError:                  # wrong ELF class, etc. -> next
                continue
    return False


def ensure_runtime():
    if sys.platform != "linux":
        return
    missing = []
    for soname in _STORE_PATTERNS:
        try:
            ctypes.CDLL(soname, mode=ctypes.RTLD_GLOBAL)
        except OSError:
            if not _preload_from_store(soname):
                missing.append(soname)
    if missing:
        raise RuntimeError(
            "could not preload " + ", ".join(missing) +
            " for lightgbm -- install gcc-libs/zlib or set LD_LIBRARY_PATH "
            "(see .env-ml for the NixOS shape)")


ensure_runtime()
