import os, configparser, time
import oci
import paramiko
from scp import SCPClient
from os import chmod

class MeanStackConfig(object):

    def __init__(self, compute):
        self.public_ip = compute.public_ip
        self.keyfile = compute.keyfile
        print 'Connecting to opc@%s ...' % (self.public_ip)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #self.client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))

    def connect(self):
        while True:
            try:
                self.client.connect(self.public_ip, username='opc', look_for_keys=False, key_filename=self.keyfile, timeout=1)
                return
            except Exception as e: 
                pass

    def execute(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                alldata = stdout.channel.recv(1024)
                while stdout.channel.recv_ready():
                    alldata += stdout.channel.recv(1024)
                print str(alldata, "utf8") 
        time.sleep(1)      
    
    def install(self):
        print 'Installing MEAN stack on opc@%s ...' % (self.public_ip)
        scp = SCPClient(self.client.get_transport())
        scp.put('./meanstack.sh')
        time.sleep(1)
        scp.close()
        self.execute('sudo chmod +x meanstack.sh')
        self.execute('./meanstack.sh')