import os, io, shutil, json
import oci
import vcn, compute, mean_stack_config, load_balancer

#megha branch

config = {'additional_user_agent': '',
    'eastgroup': 'ocid1.compartment.oc1..aaaaaaaa7hb6f2zbl6lf5nfusqiptcp3h3gzwrzfm5ejqllad5xatapeyyiq',
    'fingerprint': '6f:fb:7e:c5:21:50:8c:ed:69:9e:0b:a3:9c:89:4c:f8',
    'key_file': './oci_api_key.pem',
    'log_requests': False,
    'pass_phrase': 'terraform',
    'region': 'us-ashburn-1',
    'tenancy': 'ocid1.tenancy.oc1..aaaaaaaaxvh43eil7epawsv7nnc5ppemiqypkj6z7oznzdegkksn3aauigoa',
    'user': 'ocid1.user.oc1..aaaaaaaaib6h2j62ezwu3zn3bu75iamdr6a5by7epwnsrinq3bayzl2cysgq'} 

class Orchestration(object):
    config = oci.config.from_file()
    identity = oci.identity.identity_client.IdentityClient(config)
    compartments = identity.list_compartments(config['tenancy']).data
         

if __name__ == '__main__':
    # vcn = vcn.VCN()
    # vcn.create_vcn()
    # vcn.create_gateway()
    # vcn.create_subnet()
    # vcn.create_security_list()

    # compute = compute.Compute(config)
    # compute.launch_instance(vpn.subnets)

    # mean_stack = mean_stack_config.MeanStackConfig()
    # mean_stack.install()
    
    load_balancer = load_balancer.LoadBalancer(config)
    load_balancer.create()