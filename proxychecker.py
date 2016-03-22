#!/usr/bin/env python

from argparse import ArgumentParser
from Queue import Queue
from threading import Thread

import requests
import sys
import time


class ProxyChecker:
    def __init__(self, infile, outfile, threads = 200, verbose = False):
        self.infile = open(infile, "r")
        self.outfile = open(outfile, "w")
        self.threads = threads
        self.verbose = verbose

        self.total_scanned = 0
        self.total_working = 0
        self.original_ip = None

        # constants
        self.IP_CHECK = "https://api.ipify.org"
        self.QUEUE_STOP = "STOP"

        self.main()

    def process_proxy(self):
        try:
            while True:
                proxy = self.queue.get()
                if proxy == self.QUEUE_STOP:
                    return
                  
                self.save_valid_proxy(self.check_proxy(proxy))
                self.queue.task_done()

        except:
            pass

    def check_proxy(self, proxy, timeout = 5):
        proxies = {
                "http": "http://" + proxy,
                "https": "https://" + proxy
        }

        # see if the proxy actually works
        ip = self.get_external_ip(proxies = proxies)
        if not ip:
            return False
        
        self.total_scanned += 1
        if ip != self.original_ip:
            if self.verbose:
                print(ip)

            self.total_working += 1
                    
        return proxy

    def save_valid_proxy(self, proxy):
        if proxy:
            self.outfile.write(proxy + "\n")

    def get_external_ip(self, proxies = None):
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            if proxies:
                r = requests.get(self.IP_CHECK, proxies = proxies, headers = headers)

            else:
                r = requests.get(self.IP_CHECK, headers = headers)

        except IOError:
            return False
            
        return str(r.text)

    def main(self):
        if self.verbose:
            print("Loading proxy list from: {}".format(self.infile.name))
            print("Saving valid proxy list to: {}".format(self.outfile.name))
            print("Running: {} threads...".format(self.threads))

        self.original_ip = self.get_external_ip()

        if self.verbose:
            print("Your original external IP address is: {}".format(self.original_ip))
            print("Checking proxies...")
        
        self.queue = Queue(self.threads)

        # get all our threads ready for work
        for i in range(0, self.threads):
            thread = Thread(target = self.process_proxy)
            thread.daemon = True
            thread.start()

        self.start = time.time()

        # keep sending threads their jobs
        try:
            for proxy in self.infile:
                self.queue.put(proxy.strip())

        except KeyboardInterrupt:
            pass

        # send the `QUEUE_STOP` signal
        self.queue.put(self.QUEUE_STOP)
        if self.verbose:
            print("Closing down, please wait. ({:.2f} seconds run time)".format(time.time() - self.start))

        # give the threads time to shut down
        time.sleep(.5)

        if self.verbose:
            print("Scanned: {} proxies".format(self.total_scanned))
            print("Working: {} proxies".format(self.total_working))

        self.infile.close()
        self.outfile.close()
        sys.exit()


def CLI():
    # ugliest line of code ever
    threads_default = 200
    
    # handle all the command-line argument stuff
    parser = ArgumentParser(description = "Check a proxy list for working proxies.")
    parser.add_argument("infile", type = str, help = "input proxy list file")
    parser.add_argument("outfile", type = str, help = "output proxy list file")
    parser.add_argument("-t", "--threads", type = int, default = threads_default, help = "set the number of threads running concurrently (default {})".format(threads_default))
    parser.add_argument("-v", "--verbose", action = "store_true", help = "say lots of useless stuff (sometimes)")
    args = parser.parse_args()

    # check to see if the input file actually exists
    try:
        infile = open(args.infile, "r")
        infile.close()

    except IOError:
        print("Invalid proxy list filename.")
        sys.exit()

    proxy_checker = ProxyChecker(args.infile, args.outfile, threads = args.threads, verbose = args.verbose)


if __name__ == "__main__":
    CLI()
