from argparse import ArgumentParser
from Queue import Queue
from threading import Thread

import requests
import sys
import time


def process_proxy():
    try:
        while True:
            proxy = queue.get()
            if proxy == "STOP":
                return
            
            save_valid_proxy(check_proxy(proxy))
            queue.task_done()

    except:
        pass

def check_proxy(proxy, timeout = 5):
    proxies = {
            "http": "http://" + proxy,
            "https": "https://" + proxy
    }
    try:
        # see if the proxy actually works
        ip = get_external_ip(proxies = proxies)
        SCANNED += 1
        if ip == ORIG_IP:
            if VERBOSE:
                print(ip)

            WORKING += 1
                
            return False

    except IOError:
        return False
                
    return proxy

def save_valid_proxy(proxy):
    if proxy:
        OUT_F.write(proxy + "\n")

def get_external_ip(proxies = None):
    headers = {"User-Agent": "Mozilla/5.0"}
    if proxies:
        r = requests.get(IP_CHECK, proxies = proxies, headers = headers)

    else:
        r = requests.get(IP_CHECK, headers = headers)
        
    return str(r.text)


DEFAULT_THREADS = 200
IP_CHECK = "https://api.ipify.org"
IN_F = None
OUT_F = None
VERBOSE = False
ORIG_IP = None
SCANNED = 0
WORKING = 0


if __name__ == "__main__":
    # handle all the command-line argument stuff
    parser = ArgumentParser(description = "Check a proxy list for working proxies.")
    parser.add_argument("infile", type = str, help = "input proxy list file")
    parser.add_argument("outfile", type = str, help = "output proxy list file")
    parser.add_argument("-t", "--threads", type = int, default = DEFAULT_THREADS, help = "set the number of threads running concurrently (default {})".format(DEFAULT_THREADS))
    parser.add_argument("-v", "--verbose", action = "store_true", help = "say lots of useless stuff (sometimes)")
    args = parser.parse_args()

    try:
        IN_F = open(args.infile, "r")

    except IOError:
        print("Invalid proxy list filename.")
        sys.exit()

    OUT_F = open(args.outfile, "w")
        
    # number of threads running at once
    CONCURRENT_THREADS = args.threads

    if args.verbose:
        VERBOSE = True
        print("Loading proxy list from: {}".format(args.infile))
        print("Saving valid proxies list to: {}".format(args.outfile))
        print("Running: {} threads...".format(CONCURRENT_THREADS))
        
    # let's begin the whole process
    ORIG_IP = get_external_ip()
    if VERBOSE:
        print("Your original external IP address is: {}".format(ORIG_IP))
        print("Checking proxies...")
    
    queue = Queue(CONCURRENT_THREADS * 2)

    for i in range(0, CONCURRENT_THREADS):
        thread = Thread(target = process_proxy)
        thread.daemon = True
        thread.start()

    start = time.time()
    try:
        for proxy in IN_F:
            queue.put(proxy.strip())

        # queue.join()

    except KeyboardInterrupt:
        pass

    # make sure everything is closed down
    print("Closing down, please wait. ({} seconds run time)".format(time.time() - start))
    queue.put("STOP")

    if VERBOSE:
        print("Scanned: {} proxies".format(SCANNED))
        print("Working: {} proxies".format(WORKING))

    IN_F.close()
    OUT_F.close()
    sys.exit()
