import conjur.util.util_functions as utils
from conjur.util.os_types import OSTypes
import subprocess as sp


def _get_macos_certs():
    get_root_ca_command = ["find-certificate",
                           "-a", "-p", "/System/Library/Keychains/SystemRootCertificates.keychain"]
    data = ""
    with sp.Popen(["security"] + get_root_ca_command, stdin=sp.PIPE, stdout=sp.PIPE,
                  stderr=sp.STDOUT) as process:
        while True:
            line = process.stdout.readline()
            if not line:
                process.stdout.flush()
                break
            data += line.decode()
    return data


def _get_linux_certs():
    linux_cert_files_dir = "etc/ssl/certs/ca-certificates.crt"
    data = ""
    with open(linux_cert_files_dir, 'r') as f:
        data = f.read()
    return data


def _get_windows_certs():
    import ssl
    ctx = ssl.create_default_context()
    ctx.get_ca_certs()
    for item in ctx.cert_store_stats():
        print (item)


def get_system_certs():
    os = utils.get_current_os()
    if os == OSTypes.MAC_OS:
        return _get_macos_certs()
    if os == OSTypes.LINUX:
        return _get_linux_certs()
    if os == OSTypes.WINDOWS:
        return _get_windows_certs()


if __name__ == '__main__':
    print(_get_windows_certs())
