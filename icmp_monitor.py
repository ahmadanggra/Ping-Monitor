#!/usr/bin/python
from time import sleep
from sys import argv,exit
import os
from icmplib import ping,exceptions,utils
from tabulate import tabulate
from socket import inet_aton
from re import match
from socket import gethostbyname,error
# Used for smtp
import smtplib
from email.mime.text import MIMEText
import threading

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

def send_email(hostname):
    subject = "Host " + hostname + " Is Down"
    body = "Please check connectivity to host " + hostname
    sender = "ahmadanggra@gmail.com"
    recipients = ["ahmadanggra@gmail.com"]
    password = "smqm wwrq tpov nlup"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())

def main():
    if argv[1] == '--help' or argv[1] == '-h':
        icmp_help()
    addresses = list(map(str, argv[-1].split(',')))
    head = ['Host Address', 'Status', 'RTT']
    table = list()
    row = list()
    try:
        while(True):
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')
            for address in addresses:              
                if utils.is_ipv4_address(address):
                    host = ping(address, count = 1, timeout = 1, privileged = False, interval = 0.1)
                    row.append(host.address)
                    if host.is_alive:
                        row.append('Alive')
                        row.append(str(host.max_rtt) + ' ms')
                        table.append(list(row))
                        row.clear()
                    else:
                        row.append('Down')
                        row.append(str(host.max_rtt) + ' ms')
                        table.append(list(row))
                        row.clear()
                        email_thread = threading.Thread(target=send_email, args=(host.address,))
                        email_thread.start()
                else:
                    if hostname_resolves(address):
                        host = ping(address, count = 1, timeout = 1, privileged = False, interval = 0.1)
                        row.append(address)
                        if host.is_alive:
                            row.append('Alive')
                            row.append(str(host.max_rtt) + ' ms')
                            table.append(list(row))
                            row.clear()
                        else:
                            row.append('Down')
                            row.append(str(host.max_rtt) + ' ms')
                            table.append(list(row))
                            row.clear()
                            email_thread = threading.Thread(target=send_email, args=(host.address,))
                            email_thread.start()
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
    except Exception as e:
        print(e)
        icmp_help()