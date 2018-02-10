import os, sys, time, threading, configparser

import oci
from vcn import VCN
from compute import Compute
from load_balancer import LoadBalancer
from oci.load_balancer.load_balancer_client import LoadBalancerClient
from oci.core.compute_client import ComputeClient
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.core.models.update_route_table_details import UpdateRouteTableDetails

debug = False

if debug:
    parser = configparser.ConfigParser()
    parser.read('config')
    config = parser.defaults()
else:
    config = oci.config.from_file()

lb_client = LoadBalancerClient(config)
compute_client = ComputeClient(config)
vcn_client = VirtualNetworkClient(config)

def sleep(): time.sleep(1)

def destroy_compute_instance(instance):
    print('Destroying compute instance ...')
    compute_client.terminate_instance(instance.id)
    while True:
        try:
            if compute_client.get_instance(instance.id).data.lifecycle_state == 'TERMINATED': return
            sleep()
        except Exception as e: return

def destroy_subnet(subnet):
    print('\tDestroying subnet ...')
    vcn_client.delete_subnet(subnet.id)
    while True:
        try:
            if vcn_client.get_subnet(subnet.id).data.lifecycle_state == 'TERMINATED': return
            sleep()
        except Exception as e: return

if __name__ == '__main__':
    print('Destroying ssh keys ...')
    for filename in os.listdir('.'):
        if filename.startswith('private'):
            os.remove(filename)


    """""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""
    """                             """
    """    Destroy Load Balancer    """
    """                             """
    """""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""
    print('Destroying load balancer ...')
    lbs = lb_client.list_load_balancers(config['compartment']).data
    lb = next((x for x in lbs if x.display_name == config['display_name']), None)
    try: lb_client.delete_load_balancer(lb.id)
    except Exception as e: pass


    """""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""
    """                             """
    """  Destroy Compute Instances  """
    """                             """
    """""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""
    all_instances = compute_client.list_instances(config['compartment']).data
    instances = [x for x in all_instances if config['display_name'] in x.display_name]
    running_instances = [x for x in instances if x.lifecycle_state == 'RUNNING']
    threads = []
    for instance in running_instances: 
        thread = threading.Thread(target=destroy_compute_instance, args=(instance,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


    """""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""
    """                             """
    """         Destroy VCN         """
    """                             """
    """""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""
    print('Destroying VCN ...')
    vcns = vcn_client.list_vcns(config['compartment']).data
    vcn = next((x for x in vcns if x.display_name == config['display_name']), None)
    if vcn == None: quit()
    subnets = vcn_client.list_subnets(config['compartment'], vcn.id).data
    threads = []
    for subnet in subnets:
        thread = threading.Thread(target=destroy_subnet, args=(subnet,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    print('\tDestroying route rules ...')
    vcn_client.update_route_table(
        rt_id = vcn.default_route_table_id,
        update_route_table_details = UpdateRouteTableDetails(route_rules=[])
    )
    print('\tDestroying internet gateway ...')
    gateways = vcn_client.list_internet_gateways(config['compartment'], vcn.id).data
    if len(gateways) > 0:
        gateway = gateways[0]
        vcn_client.delete_internet_gateway(gateway.id)
        while True:
            try:
                if vcn_client.get_internet_gateway(gateway.id).data.lifecycle_state == 'TERMINATED': break
                sleep()
            except Exception as e:
                if len(vcn_client.list_internet_gateways(config['compartment'], vcn.id).data) == 0: break
                sleep()
    vcn_client.delete_vcn(vcn.id)

    """
        print('Deleting %s compute instances ...' % (len(vcn.subnets)))
        for i, subnet in enumerate(vcn.subnets[0:2]):
            compute = Compute(config, subnet, instance_config)
            compute.terminate_instance()
    """