import os, io, shutil, json, threading
import oci
from configparser import ConfigParser
from vcn import VCN
from compute import Compute
from mean_stack_config import MeanStackConfig
from load_balancer import LoadBalancer

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
    vnic = compute.get_vnic(vcn)
    mean_stack = MeanStackConfig(compute)
    mean_stack.install()

if __name__ == '__main__':

    vcn = VCN(config)
    vcn.create_vcn()
    vcn.create_gateway()
    vcn.create_route_rules()
    vcn.create_subnets()
    vcn.create_security_rules()

    threads = []
    for subnet in vcn.subnets[0:2]:
        thread = threading.Thread(target=install_mean_stack, args=(subnet, vcn,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    lb = LoadBalancer(config, vcn)
    lb.create_load_balancer()
    lb.create_backend_set()
    lb.create_backends()
    lb.create_listener()
    print('MEAN Stack URL: http://' + lb.public_ip + ':8080')