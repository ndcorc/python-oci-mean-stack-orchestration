import os, io, shutil, json, threading
import oci
from configparser import ConfigParser
from orchestration import *
#from vcn import VCN
#from compute import Compute
#from mean_stack_config import MeanStackConfig
#from load_balancer import LoadBalancer

debug = False

if debug:
    parser = ConfigParser()
    parser.read('config')
    config = parser.defaults()
else:
    config = oci.config.from_file()

def install_mean_stack(subnet, vcn):
    compute = Compute(config, subnet)
    compute.launch_instance()
    compute.get_vnic(vcn)
    mean_stack = MeanStackConfig(compute)
    mean_stack.connect()
    mean_stack.install()

"""
subnet = vcn.subnets[0]
compute = Compute(config, subnet)
compute = Compute(config, subnet)
compute.launch_instance()
compute.get_vnic(vcn)
#self.public_ip = compute.public_ip
#self.keyfile = compute.keyfile
print('Connecting to opc@%s ...' % (compute.public_ip))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))

try:
    while True:
        try:
            client.connect(compute.public_ip, username='opc', look_for_keys=False, key_filename=compute.keyfile)
            break
        except Exception as e:
            pass
except Exception as e:
    pass
mean_stack.client.connect(mean_stack.public_ip, username='opc', look_for_keys=False, user_agent key_filename=mean_stack.keyfile, timeout=1)
"""

def join_threads(threads):
    for thread in threads:
        thread.join()

if __name__ == '__main__':

    vcn = VCN(config)
    vcn.create_vcn()
    vcn.create_gateway()
    vcn.create_route_rules()

    subnet_threads = []
    for ad in ['ad_1', 'ad_2']:
        thread = threading.Thread(target=vcn.create_subnet, args=(ad,))
        subnet_threads.append(thread)
        thread.start()
    join_threads(subnet_threads)
    vcn.create_security_rules()

    install_threads = []
    for subnet in vcn.subnets:
        thread = threading.Thread(target=install_mean_stack, args=(subnet, vcn,))
        install_threads.append(thread)
        thread.start()
    join_threads(install_threads)

    lb = LoadBalancer(config, vcn)
    lb.create_load_balancer()
    lb.create_backend_set()
    lb.create_backends()
    lb.create_listener()
    print 'MEAN Stack URL: http://' + lb.public_ip + ':8080'