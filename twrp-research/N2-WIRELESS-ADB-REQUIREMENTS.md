# N2 wireless ADB feature specification — 2026-10-12

Target GUI: Advanced > Network (Xoom), below Wi-Fi credentials/status.
Desired controls: Wireless ADB toggle (off by default), TCP port entry (default 5555, configurable 1024–65535), current IP:port endpoint, authenticated authorization status.

Safety gate: do not allow enable unless BOTH Wi-Fi WPA COMPLETED + IPv4 present AND ADB peer authentication successfully configured and tested. Do not expose the recovery's current unprotected root adbd over TCP. As of inspection, current N1 on Xoom reported ro.secure=0 and no positive proof of ro.adb.secure=1, so direct 'adb tcpip' is forbidden.

On enable: validate port and avoid conflicting listeners; secure authentication required; bind only to intended Wi-Fi interface when supported; show endpoint. Never spawn command with sensitive keys in argv/log. Explicitly notify user that enabling remote debugging grants privileged access to an authorized host.

On disable: shut down only the network ADB listener, preserve USB ADB. On Wi-Fi loss: stop listener; do not automatically re-enable on reconnection. Boot defaults off. Network port selection stays a nonsecret in-memory GUI value unless user requests persistence.

Security validation: inspect this legacy /sbin/adbd authentication support, build authenticated adbd if missing, test unauthorized client rejection AND authorized key acceptance on hardware, ensure no unauthenticated root listener; verify port closure and USB ADB survives all transitions. Do not enable until verified.

Status: requirements and nonfunctional read-only GUI draft saved; NO wireless TCP listener created; N1 running, no flashing or internal writes.
