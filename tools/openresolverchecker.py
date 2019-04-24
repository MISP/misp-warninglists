#!/usr/bin/env python3
# Tool to check for openresolvers (from list of source IP).
#
# Dragon Research Group project
#
# Software is free software released under the "Modified BSD license"
#
# Copyright (c) 2015 Alexandre Dulaunoy - a@foo.be
#
# Has been modified by Edvard Rejthar, CSIRT.cz at MISP Hackathon 7 Dec 2016
#
#
import os, sys, argparse, redis, datetime, ipdb, json, threading, jsonpickle
from dns.resolver import Resolver, NXDOMAIN, NoNameservers, Timeout
from urllib.request import urlopen
from netaddr import IPAddress, AddrFormatError
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger('openresolverchecker')
__help__ = """
Check the list of IP/domains agains an IP to see where is open resolvers.

Examples:
./openresolverchecker.py 
./openresolverchecker.py --max 2000 --out save.json --include-timeouts
./openresolverchecker.py -v -o save.json --type TXT --query resolvertest.switch.ch "resolver test ok" 
./openresolverchecker.py -v -o save.json --type A --query seznam.cz 77.75.77.53 --input ../list.json --max 100

"""

DEFAULT_QUERY, DEFAULT_IP = "resolvertest.switch.ch", "resolver test ok"
MISP_WARNING_LIST = "https://raw.githubusercontent.com/MISP/misp-warninglists/master/lists/public-dns-v4/list.json"

class OpenResolverChecker:
    def __init__(self, ips, query = DEFAULT_QUERY, expected = DEFAULT_IP, threadnum = 500, verbose = 0, recordType = "TXT", includeTimeouts = False ):
        self.resolver = Resolver()
        self.resolver.timeout=1
        self.resolver.lifetime=1
        self.query = query
        self.expected = expected
        self.openresolvers = [] # [address, ...]
        self.errors = [] # [(address, errcode), ...]
        self.ips = ips                    
        self.threadnum = threadnum                
        self.verbose = verbose
        self.recordType = recordType
        self.includeTimeouts = includeTimeouts

    def _worker(cls,num, this):
        """ Worker thread checks if the IP is an Open resolver. """
        while True:                                  
            try:
                ip = this.ips.pop()
            except IndexError:
                return False
            
            ts = str(datetime.datetime.utcnow())
            
            try:
                IPAddress(ip) # check
                addresses = [ip]
            except AddrFormatError:  
                addresses = []
                try:
                    answer = dns.resolver.query(ip, 'AAAA')
                    for data in answer: 
                        addresses.append(data)
                    answer = dns.resolver.query(ip, 'A')
                    for data in answer: 
                        addresses.append(data)
                except:
                    #logging.warning("Cant translate to the IP: {}".format(ip))
                    this.errors.append((ip, "untranslatable"))
                    if this.verbose > 0:
                        print("Left:{} (Worker {}) {} {}".format(len(this.ips), num, "untranslatable", ip))
                    continue
            
            for ip in addresses:
                passed, msg = this.check(address=ip)                
                #if passed:
                    #this.openresolvers.append(ip)                
                    #logline = ts+" - Open resolver at "+ip+" "+str(tst)                
                #else:
                    #logline = "{} closed".format(ip)                
                if this.verbose > 0:
                    print("Left:{} (Worker {}) {} {}".format(len(this.ips), num, msg, ip))
            
    
    def launch(self):
        """ Launch analysis in threads. """
        threads = []        
        for i in range(self.threadnum):
            th = threading.Thread(target=self._worker, args=(i,self))
            threads.append(th)
            th.start()

        for x in threads:
            x.join()

        return self.openresolvers

    
    def check(self, address=None):
        """ False : not an openresolver
        True is an open resolver
        (True, ip) is an open resolver and includes the non expected A record """
        if address is None:
            return None                
                        
        self.resolver.nameservers=[address]
        try:            
            #print("QUERY",self.query, self.recordType)             
            answer = self.resolver.query(self.query, self.recordType)
            result = next(answer.__iter__()).to_text().strip('"')            
            if result == self.expected:
                self.openresolvers.append(address)
                return (True, "*** open resolver")
            else:
                self.errors.append((address, "Wrong answer: {}".format(txt)))
                return (False, "Wrong answer: {}".format(txt))
        except Timeout as e:            
            if not self.includeTimeouts:                
                return (False, "Timeout")
            else:
                ex = e
        except Exception as e:                        
            ex = e
            # NXDOMAIN = lies that the know domain does not exist                        
            # NoNameservers = Refused – they claim to be but are not. Ex ns1.eurodns.com", 80.92.65.2
            # any other reason
            pass        
        self.errors.append((address, ex.__class__.__name__))
        return (False, ex.__class__.__name__)
    
if __name__ == "__main__":    
    # command line args
    parser = argparse.ArgumentParser(description=__help__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-q','--query', help='<query> <expected ip> EX: {} {}'.format(DEFAULT_QUERY, DEFAULT_IP),nargs=2, default=(DEFAULT_QUERY, DEFAULT_IP))    
    parser.add_argument('-o','--out', help='output file to store the list of open resolvers')
    parser.add_argument('-v','--verbose', help='verbose output', action="count", default = 0)
    parser.add_argument('--type', help='Specify the type of record we\'re checking. Default is TXT record but you might want to use an A record.', default="TXT")
    parser.add_argument('--include-timeouts', help='Include timeout exception to error results. Normally, only Nxdomain and NoNameservers exceptions are treated as errors.', action="store_true")
    parser.add_argument('-m','--max', help='max open resolvers to check (IE. only first 100)', type=int)
    parser.add_argument('-t','--threadnum', help='thread number (default 500)', type=int, default=500)
    parser.add_argument('-i','--input', help="Source file in the format: {'list':[ip, domain...]}. If no file is given, MISP "+MISP_WARNING_LIST+" will be used instead.", default=None)            
    args = parser.parse_args()        
        
    # load resolvers list    
    if args.input:
        try: # local file
            with open(args.input) as f:
                sourceFile = json.load(f)
        except FileNotFoundError:
            sys.exit("File {} not found.".format(args.input))
    else: # load from github       
        print("Downloading the list from: {}".format(MISP_WARNING_LIST))
        response = urlopen(MISP_WARNING_LIST)
        sourceFile = json.loads(response.read().decode('utf-8'))
        
    
    ips = sourceFile["list"]                
    if args.max:
        ips = ips[:args.max]
    count = len(ips)
    if not count:
        print("Nothing to be checked, empty list.")
        quit()                          
    
    # launch resolvers
    orc = OpenResolverChecker(ips, args.query[0], args.query[1], threadnum = args.threadnum, verbose = args.verbose, recordType=args.type, includeTimeouts = args.include_timeouts)
    orc.launch()
        
    # work with results
    if args.out: # save to file
        with open(args.out, "w") as f:
            sourceFile.update({"timestamp": str(datetime.datetime.utcnow()), 
                               "openresolvers": orc.openresolvers,                                
                               "ip-checked": count, 
                               "open-ratio": (len(orc.openresolvers)/count),  
                               "query": args.query[0], 
                               "query-expected-ip": args.query[1],
                               "query-record-type": args.type,
                               "errors": orc.errors
                               })            
            json.dump(sourceFile, f, indent=4, sort_keys = True)            
    else: # print to stdout
        print("Valid resolvers:")
        print(orc.openresolvers)    
    print("Resolvers checked: {}, opens: {} ({} %), errors {} ({} %)".format(count,                                                                                 len(orc.openresolvers), (len(orc.openresolvers)/count)*100 ,len(orc.errors),(len(orc.errors)/count*100)))
