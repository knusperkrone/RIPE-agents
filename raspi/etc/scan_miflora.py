from miflora import miflora_poller
from btlewrap.bluepy import BluepyBackend
import multiprocessing 
import sys

def check(mac):
    poller = miflora_poller.MiFloraPoller(mac, BluepyBackend)

    try:
        poller.clear_cache()
        poller.fill_cache()
    except Exception:
        return
    
    print(f'\rFound {mac} with version {poller.firmware_version()}')
    sys.exit(0)

def main():
    macs = [
        mac.upper()
        for (mac, name) in BluepyBackend.scan_for_devices(10)
    ]
    macs.sort()

    for (i, mac) in enumerate(macs):
        print(f'\rDevice {i + 1}/{len(macs)} {mac} ', end='', flush=True)
        p = multiprocessing.Process(target=check, args=[mac])
        p.start()
        p.join(10)
        p.kill()
    sys.exit(1)
        

if __name__ == '__main__':
    main()