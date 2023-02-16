from time import sleep
from sys import argv,exit
from os import system
from icmplib import ping,exceptions,utils
from tabulate import tabulate
from socket import inet_aton
from re import match
from socket import gethostbyname,error

# usage icmp_monitor <<update in second>> << list of ip address separate by comma (,)
# example python icmp_monitor.py 192.168.0.1,192.168.0.2
def icmp_help():  
    print('Usage:')
    print('python icmp_monitor.py [update ping in second] [list of ip address/hostname separated by comma.]')
    exit()    

def hostname_resolves(hostname):
    try:
        gethostbyname(hostname)
        return 1
    except error:
        return 0

def main():
    if argv[1] == '--help' or argv[1] == '-h':
        icmp_help()
    addresses = list(map(str, argv[-1].split(',')))
    head = ['Host Address', 'Status', 'RTT']
    table = list()
    row = list()
    try:
        while(True):
            system('cls')
            for address in addresses:              
                if utils.is_ipv4_address(address):
                    host = ping(address, count = 1, timeout = 1)
                    row.append(host.address)
                    if host.is_alive:
                        row.append('Alive')
                        row.append(str(host.max_rtt) + ' ms')
                        table.append(list(row))
                        row.clear()
                    else:
                        row.append('Down')
                        row.append(host.max_rtt)
                        table.append(list(row))
                        row.clear()
                else:
                    if hostname_resolves(address):
                        host = ping(address, count = 1, timeout = 1)
                        row.append(address)
                        if host.is_alive:
                            row.append('Alive')
                            row.append(str(host.max_rtt) + ' ms')
                            table.append(list(row))
                            row.clear()
                        else:
                            row.append('Down')
                            row.append(host.max_rtt)
                            table.append(list(row))
                            row.clear()
                    else:
                        row.append(address)
                        row.append('DNS query failed for')
                        row.append('N/A')
                        table.append(list(row))
                        row.clear()
            print(tabulate(table, headers=head, tablefmt='grid'))
            table.clear()
            sleep(int(argv[1]))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__' :
    try:
        
        if len(argv) == 3:
            main()
        else:
            raise Exception('Parameter kurang')
    except Exception:
        icmp_help()