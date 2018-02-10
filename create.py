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
    compute.get_vnic(vcn)
    mean_stack = MeanStackConfig(compute)
    mean_stack.install()

"""
compute = Compute(config, subnet)
compute_details = LaunchInstanceDetails(
    availability_domain = compute.subnet.availability_domain,
    compartment_id = compute.config['compartment'],
    display_name = compute.name,
    image_id = compute.operating_systems[config['image_os']],
    shape = config['shape'],
    subnet_id = compute.subnet.id,
    metadata = compute.create_metadata()
)
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
    print('MEAN Stack URL: http://' + lb.public_ip + ':8080')