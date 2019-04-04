#!/usr/bin/env python
import json
import socket
import os
import sys
import filelock
import re
import psutil
import datetime
import subprocess
import argparse

class check_hardware():
    def __init__(self,args):
        """
        ARGS
        
        """ 
        self.Hp_check_cmd = "/usr/local/nrpe/libexec/check_hpasm"
        self.dmidecode_cmd = "dmidecode"
        self.start_ts = int(datetime.datetime.now().strftime("%s"))
        self.lockfile = "/var/run/v2_check_hardware.lock"
        lock_require=self.lock_acquire()
        lock_require
        get_manufacturer=self.get_manufacturer()
        get_manufacturer
        if get_manufacturer == "hp":
            """
            Execute HP check

            """
            if socket.gethostname().find('db')>=0 and args.storage:
                out = subprocess.Popen([str(self.Hp_check_cmd), '--only-disks'], stdout=subprocess.PIPE)
            else:
                if args.cpu:
                    out = subprocess.Popen([str(self.Hp_check_cmd), '--only-cpu'], stdout=subprocess.PIPE)
                elif args.memory:
                    out = subprocess.Popen([str(self.Hp_check_cmd), '--only-memory'], stdout=subprocess.PIPE)
                if args.storage:
                    out = subprocess.Popen([str(self.Hp_check_cmd), '--only-disks', 'daacb'], stdout=subprocess.PIPE)
                elif args.power:
                    out = subprocess.Popen([str(self.Hp_check_cmd), '--only-power'], stdout=subprocess.PIPE)
                if args.fan:
                    out = subprocess.Popen([str(self.Hp_check_cmd), '--only-fans'], stdout=subprocess.PIPE)
                elif args.temp:
                    out = subprocess.Popen([str(self.Hp_check_cmd), '--only-temperature'], stdout=subprocess.PIPE)
                if args.all_info:
                    out = subprocess.Popen([str(self.Hp_check_cmd), 'j\ --blacklist', 'daacb'], stdout=subprocess.PIPE)
                stdout = out.communicate()[0]
                stdout = str(stdout).strip("\n")
                print (stdout)
                self.get_model()
        """
        protect check from multiple access

        """
    def lock_acquire(self):
        if  os.path.getsize(self.lockfile) > 0:
            exists = True
            with open(self.lockfile, "r") as lock_file:
                data = (lock_file.read())
                if not psutil.pid_exists(int(data)):
                    open(self.lockfile, 'w').close()
            while  exists :
                if not psutil.pid_exists(int(data)):
                    open(self.lockfile, 'w').close()
                    break
                now = int(datetime.datetime.now().strftime("%s"))
                delta = now - self.start_ts
                print (now)
                if delta > 60:
                    sys.stderr.write('Lock acquisition timeout')
                    sys.exit(3)
                    time.sleep( 1 )
        file = open(self.lockfile, "a")
        file.write(str(os.getpid()))
        file.close()
    """
    Get model of server
    """   
    def get_model(self):
        count = 0
        out = subprocess.Popen([str(self.dmidecode_cmd), '-s', 'system-product-name'], stdout=subprocess.PIPE)
        stdout = out.communicate()[0]
        stdout = str(stdout).strip("\n")
        for i in stdout:
            if i == ' ':
                count += 1
        if count == 0:    
            self.Model = stdout
            print (self.Model)
        elif count == 3:
            self.Model = stdout.split(" ")[1]
            #print (self.Model)

    """
    Get get_manufacturer
    """
    def get_manufacturer(self):
        cmd = "dmidecode |grep Vendor"
        out = subprocess.Popen(str(cmd),shell=True,stdout=subprocess.PIPE)
        stdout = out.communicate()[0]
        stdout = str(stdout).strip("\n")
        if "HP" in stdout:
            Manufacturer = "hp"
        elif "Dell" in stdout:
            Manufacturer = "dell"
        else:
            Manufacturer = "unknown model"
            sys.stderr.write('Uknown Model')
            sys.exit(3)
        return(Manufacturer)
 
def main():
    parser = argparse.ArgumentParser(
        description='check hardware',
        add_help=True
    )
    parser.add_argument('--cpu', action="store_true",
                        help='check cpu health')
    parser.add_argument('--memory', action="store_true",
                        help='check memory health')
    parser.add_argument('--fan', action="store_true",
                        help='check fans health')
    parser.add_argument('--temp', action="store_true",
                        help='check temperature')
    parser.add_argument('--power', action="store_true",
                        help='check power supply health')
    parser.add_argument('--storage', action="store_true",
                        help='check LD/PD/RAID health')
    parser.add_argument('--all_info', action="store_true",
                        help='check global health status of server')
    args = parser.parse_args()
    check_hardware(args)
if __name__ == '__main__':
    main()
