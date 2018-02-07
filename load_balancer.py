import configparser
import os, time

import oci
from oci.load_balancer.load_balancer_client import LoadBalancerClient
from oci.load_balancer.models.create_load_balancer_details import CreateLoadBalancerDetails
from oci.load_balancer.models.health_checker_details import HealthCheckerDetails
from oci.load_balancer.models.create_backend_set_details import CreateBackendSetDetails
from oci.load_balancer.models.create_backend_details import CreateBackendDetails
from oci.load_balancer.models.create_listener_details import CreateListenerDetails

class LoadBalancer(object):

    def __init__(self, config, subnets, instance_config=None):
        self.config = config
        self.instance_config = configparser.RawConfigParser()
        self.instance_config.read('instance_config')
        self.client = LoadBalancerClient(config)
        self.subnet_ids = [subnet.id for subnet in subnets]
        if instance_config != None:
            self.lb_id = instance_config['LOAD_BALANCER']['lb_id']
            self.public_ip = instance_config['LOAD_BALANCER']['public_ip']

    def create_load_balancer(self):
        print('Creating load balancer ...')
        load_balancer_details = CreateLoadBalancerDetails(
            compartment_id = self.config['compartment'],
            display_name = self.config['display_name'],
            shape_name = self.config['lb_shape'],
            subnet_ids = self.subnet_ids
        )
        self.client.create_load_balancer(load_balancer_details)
        while True:
            for lb in self.client.list_load_balancers(self.config['compartment']).data:
                if lb.display_name == self.config['display_name'] and lb.lifecycle_state == 'ACTIVE':
                    self.lb_instance = lb
                    self.public_ip = lb.ip_addresses[0].ip_address
                    return
            time.sleep(5)

    def delete_load_balancer(self):
        print('Deleting load balancer ...')
        self.client.delete_load_balancer(self.lb_id)

    def create_backend_set(self):
        health_checker_details = HealthCheckerDetails(
            port = 8080,
            protocol = 'HTTP',
            response_body_regex='.*',
            return_code = 200,
            url_path = '/'
        )
        backend_set_details = CreateBackendSetDetails(
            health_checker = health_checker_details,
            name = self.config['backend_set_name'],
            policy = 'ROUND_ROBIN'
        )
        self.client.create_backend_set(backend_set_details, self.lb_instance.id).data
        
    def create_backends(self):
        for i in range(len(self.subnet_ids))[0:2]:
            private_ip = self.instance_config['COMPUTE'+str(i+1)]['private_ip']
            backend_details = CreateBackendDetails(
                ip_address = private_ip,
                port = 8080
            )
            self.client.create_backend(backend_details, self.lb_instance.id, self.config['backend_set_name'])
        while True:
            try:
                self.backends = self.client.list_backends(self.lb_instance.id, self.config['backend_set_name']).data
            except Exception as e: 
                continue
            while len(self.backends) < 3:
                self.backends = self.client.list_backends(self.lb_instance.id, self.config['backend_set_name']).data
                time.sleep(1)
            return

    def create_listener(self):
        listener_details = CreateListenerDetails(
            default_backend_set_name = self.config['backend_set_name'],
            name = self.config['listener_name'],
            port = 8080,
            protocol = 'HTTP'
        )
        self.client.create_listener(listener_details, self.lb_instance.id)
        time.sleep(10)

    def create_instance_config(self):
        section = 'LOAD_BALANCER'
        config = configparser.RawConfigParser()
        config.add_section(section)
        config.set(section, 'lb_id', self.lb_instance.id)
        config.set(section, 'public_ip', self.public_ip)
        with open('instance_config', 'a') as configfile:
            config.write(configfile)