import os, configparser

import oci
from vcn import VCN
from compute import Compute
from load_balancer import LoadBalancer

if __name__ == '__main__':
    parser = configparser.ConfigParser()
    parser.read('config')
    config = parser.defaults()
    instance_config = configparser.RawConfigParser()
    instance_config.read('instance_config')

    vcn = VCN(config, instance_config)
    lb = LoadBalancer(config, vcn.subnets, instance_config)
    
    lb.delete_load_balancer()

    print('Deleting %s compute instances ...' % (len(vcn.subnets)))
    for i, subnet in enumerate(vcn.subnets):
        compute = Compute(config, subnet, instance_config)
        compute.terminate_instance()
        os.remove('private'+str(i+1)+'.pem')

    vcn.delete_subnets()
    vcn.delete_route_rules()
    vcn.delete_internet_gateway()
    vcn.delete_vcn()