import os, io, shutil, json
import oci
import vcn, compute, mean_stack_config, load_balancer

class Orchestration(object):
    config = oci.config.from_file()
    identity = oci.identity.identity_client.IdentityClient(config)
    compartments = identity.list_compartments(config['tenancy']).data
        

if __name__ == '__main__':
    vcn = vcn.VCN()
    vcn.create_vcn()
    vcn.create_gateway()
    vcn.create_subnet()
    vcn.create_security_list()

    compute = compute.Compute(config)
    compute.launch_instance(vpn.subnets)

    mean_stack = mean_stack_config.MeanStackConfig()
    mean_stack.install()
    
    load_balancer = load_balancer.LoadBalancer(config)
    load_balancer.create()