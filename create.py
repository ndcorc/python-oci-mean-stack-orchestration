import os, io, shutil, json, threading
import oci
from configparser import ConfigParser
from vcn import VCN
from compute import Compute
from mean_stack_config import MeanStackConfig
from load_balancer import LoadBalancer

def install_mean_stack(config, subnet, vcn):
    compute = Compute(config, subnet)
    compute.launch_instance()
    compute.get_vnic(vcn)
    compute.create_instance_config()
    section = 'COMPUTE' + subnet.availability_domain[-1]
    mean_stack = MeanStackConfig(section)
    mean_stack.install()

if __name__ == '__main__':
    #parser = ConfigParser()
    #parser.read('config')
    #config = parser.defaults()
    config = oci.config.from_file()

    vcn = VCN(config)
    vcn.create_vcn()
    vcn.create_gateway()
    vcn.create_route_rules()
    vcn.create_subnets()
    vcn.create_security_rules()
    vcn.create_instance_config()

    threads = []
    for subnet in vcn.subnets:
        thread = threading.Thread(target=install_mean_stack, args=(config, subnet, vcn,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    lb = LoadBalancer(config, vcn.subnets)
    lb.create_load_balancer()
    lb.create_backend_set()
    lb.create_backends()
    lb.create_listener()
    lb.create_instance_config()
    print('MEAN Stack URL: http://' + lb.public_ip + ':8080')