#!/usr/bin/python
# Module for ping
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
# For config parse
import configparser

# for data please define data in data.ini
# usage icmp_monitor <<update in second>> << list of ip address separate by comma (,) >>
# or icmp_monitor <<update in second>> -f or --file
# example python icmp_monitor.py 5 192.168.0.1,192.168.0.2
# example python icmp_monitor.py 5 -f
# to email if host/ip down add -s or --sendmail on last argument
# example python icmp_monitor.py 5 192.168.0.1,192.168.0.2 --sendmail
# example python icmp_monitor.py 5 -f -s
def icmp_help():  
    print('Usage:')
    print('python icmp_monitor.exe [interval] [list of ip address/hostname separated by comma.]')
    print('python icmp_monitor.exe [interval] [list of ip address/hostname separated by comma.] [-s or --sendmail]')
    print('python icmp_monitor.exe [interval] [-f or --file]')
    print('python icmp_monitor.exe [interval] [-f or --file] [-s or --sendmail]')
    exit()    

def hostname_resolves(hostname):
    try:
        gethostbyname(hostname)
        return 1
    except error:
        return 0

def send_email(hostname,sndr,rcpt,passwd):
    subject = "Host " + hostname + " Is Down"
    body = "Please check connectivity to host " + hostname
    sender = sndr
    recipients = rcpt.split(',')
    password = passwd
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())

def icmp_ping():
    # reading parameter
    if argv[1] == '--help' or argv[1] == '-h':
        icmp_help()
    if argv[2] == '--file' or argv[2] == '-f':
        # Create a parser object
        config = configparser.ConfigParser()
        # Read the configuration file
        config.read('data.ini')
        # Get the string of IPs from the 'ips' key under the 'ip' section
        ips_string = config.get('ip', 'ips')
        # Split the string by commas and create a list of IPs
        #addresses = [ip.strip() for ip in ips_string.split(',')]
        addresses = ips_string.split(',')
    if ',' in argv[2]:   
        addresses = list(map(str, argv[2].split(',')))
    # reading smtp config if -s or --sendmail defined as argument
    if argv[-1] == '--sendmail' or argv[-1] == '-s':
        # Create a parser object
        config = configparser.ConfigParser()
        # Read the configuration file
        config.read('data.ini')
        # Access the value for 'sender' under the 'email' section
        sender = config.get('email', 'sender')
        recipients = config.get('email', 'recipients')
        password = config.get('email', 'password')        
    
    # table format 
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
                        if argv[-1] == '--sendmail' or argv[-1] == '-s':
                            email_thread = threading.Thread(target=send_email, args=(host.address,sender,recipients,password,))
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
                            if argv[-1] == '--sendmail' or argv[-1] == '-s':
                                email_thread = threading.Thread(target=send_email, args=(host.address,sender,recipients,password,))
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

def main():
    icmp_ping()

if __name__ == '__main__' :
    try:
        # for script using comma
        if len(argv) == 3 and ',' in argv[2] and  argv[1].isdigit():
            main()
        elif len(argv) == 4 and ',' in argv[2] and  argv[1].isdigit() and ('-s' == argv[-1] or '--sendmail' == argv[-1]):
            main()
        # for script using file
        elif len(argv) == 3 and ('-f' == argv[2] or '--file' == argv[2]) and  argv[1].isdigit():
            print('test')
            main()
        elif len(argv) == 4 and ('-f' == argv[2] or '--file' == argv[2]) and  argv[1].isdigit() and ('-s' == argv[-1] or '--sendmail' == argv[-1]):
            main()
        else:
            raise exceptions('Illegal parameter')
    except :
        icmp_help()