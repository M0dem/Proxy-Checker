#!/usr/bin/env python

from argparse import ArgumentParser
from Queue import Queue
from threading import Thread

import requests
import sys
import time


class ProxyChecker:
    def __init__(self, inlist, threads = 200, verbose = False, timeout = 25):
        self.inlist = inlist
        # there shouldn't be more threads than there are proxies
        if threads > len(self.inlist):
            self.threads = len(self.inlist)

        else:
            self.threads = threads

        self.verbose = verbose
        self.timeout = timeout

        self.outlist = []
        self.total_scanned = 0
        self.total_working = 0
        self.original_ip = None
        self.threads_done = 0

        # constants
        self.IP_CHECK = "https://api.ipify.org"

    def save_valid_proxy(self, proxy):
        if proxy:
            self.outlist.append(proxy)

    def get_external_ip(self, proxies = None):
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            if proxies:
                r = requests.get(self.IP_CHECK, proxies = proxies, headers = headers, timeout = self.timeout)

            else:
                r = requests.get(self.IP_CHECK, headers = headers)

        except IOError:
            return False

        return str(r.text)

    def check_proxy(self, proxy):
        proxies = {
                "http": "http://" + proxy,
                "https": "https://" + proxy
        }

        # see if the proxy actually works
        ip = self.get_external_ip(proxies = proxies)
        if not ip:
            return False

        if ip != self.original_ip:
            if self.verbose:
                print(ip)

            self.total_working += 1

        return proxy

    def process_proxy(self):
        try:
            while True:
                proxy = self.queue.get()
                self.save_valid_proxy(self.check_proxy(proxy))
                self.queue.task_done()
                self.total_scanned += 1

        except:
            pass

    def start(self):
        if self.verbose:
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
            for proxy in self.inlist:
                self.queue.put(proxy.strip())

            self.queue.join()

        except KeyboardInterrupt:
            if self.verbose:
                print("Closing down, please let the threads finish.")

        if self.verbose:
            print("Running: {:.2f} seconds".format(time.time() - self.start))

        if self.verbose:
            print("Scanned: {} proxies".format(self.total_scanned))
            print("Working: {} proxies".format(self.total_working))

        return self.outlist


def CLI():
    threads_default = 200
    timeout_default = 25

    # handle all the command-line argument stuff
    parser = ArgumentParser(description = "Check a proxy list for working proxies.")
    parser.add_argument("infile", type = str, help = "input proxy list file")
    parser.add_argument("outfile", type = str, help = "output proxy list file")
    parser.add_argument("-t", "--threads", type = int, default = threads_default, help = "set the number of threads running concurrently (default {})".format(threads_default))
    parser.add_argument("-v", "--verbose", action = "store_true", help = "say lots of useless stuff (sometimes)")
    parser.add_argument("-to", "--timeout", type = int, help = "the timeout for testing proxies (default {})".format(timeout_default))
    args = parser.parse_args()

    # check to see if the input file actually exists
    try:
        infile = open(args.infile, "r")
        inlist = infile.read().split("\n")
        infile.close()

    except IOError:
        print("Invalid proxy list filename.")
        sys.exit()

    proxy_checker = ProxyChecker(inlist, threads = args.threads, verbose = args.verbose, timeout = timeout_default)
    outlist = proxy_checker.start()
    outfile = open(args.outfile, "w")
    outfile.write("\n".join(outlist))
    outfile.close()


if __name__ == "__main__":
    CLI()
