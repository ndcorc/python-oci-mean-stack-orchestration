import os, configparser, time
import oci
import paramiko
from scp import SCPClient
from os import chmod

class MeanStackConfig(object):

    def __init__(self, section):
        parser = configparser.ConfigParser()
        parser.read('config')
        self.config = parser.defaults()
        self.instance_config = configparser.RawConfigParser()
        self.instance_config.read('instance_config')
        #self.public_ip = compute_ip
        self.public_ip = self.instance_config[section]['public_ip']
        self.keyfile = self.instance_config[section]['keyfile']
        print('Connecting to opc@%s ...' % (self.public_ip))
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        while True:
            try:
                self.client.connect(self.public_ip, username='opc', look_for_keys=False, key_filename=self.keyfile, timeout=1)
            except Exception as e: continue
            break

    def execute(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                alldata = stdout.channel.recv(1024)
                while stdout.channel.recv_ready():
                    alldata += stdout.channel.recv(1024)
                print(str(alldata, "utf8"))  
        time.sleep(1)      
    
    def install(self):
        print('Installing MEAN stack on opc@%s ...' % (self.public_ip))
        scp = SCPClient(self.client.get_transport())
        scp.put('./meanstack.sh')
        time.sleep(1)
        scp.close()
        self.execute('sudo chmod +x meanstack.sh')
        self.execute('./meanstack.sh')

"""

import os, configparser
import oci
import paramiko

parser = configparser.ConfigParser()
parser.read('config')
config = parser.defaults()
instance_config = configparser.RawConfigParser()
instance_config.read('instance_config')
public_ip = instance_config['COMPUTE']['public_ip']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
client.connect(public_ip, username='opc', look_for_keys=False, key_filename='./private.pem', timeout=5)

from scp import SCPClient
print('Installing MEAN stack on opc@%s ...\n' % (mean_stack.public_ip))
scp = SCPClient(mean_stack.client.get_transport())
scp.put('./meanstack.sh')
scp.close()
stdin, stdout, stderr = mean_stack.client.exec_command('sudo chmod +x meanstack.sh')
stdin, stdout, stderr = mean_stack.client.exec_command('./meanstack.sh')

"""