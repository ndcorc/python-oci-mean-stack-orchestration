from configparser import ConfigParser

import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.core.models.create_vcn_details import CreateVcnDetails
from oci.core.models.create_internet_gateway_details import CreateInternetGatewayDetails
from oci.core.models.route_rule import RouteRule
from oci.core.models.update_route_table_details import UpdateRouteTableDetails
from oci.core.models.create_subnet_details import CreateSubnetDetails
from oci.core.models.port_range import PortRange
from oci.core.models.tcp_options import TcpOptions
from oci.core.models.ingress_security_rule import IngressSecurityRule
from oci.core.models.update_security_list_details import UpdateSecurityListDetails

class VCN(object):

    def __init__(self, config, instance_config=None):
        self.config = config
        self.instance_config = instance_config
        self.client = VirtualNetworkClient(config)
        self.subnets = []
        self.route_rules = []
        self.security_rules = []
        if instance_config != None:
            self.vcn_id = instance_config['VCN']['vcn_id']
            self.gateway_id = instance_config['VCN']['gateway_id']
            self.rt_id = instance_config['VCN']['rt_id']
            self.subnets.append(self.client.get_subnet(instance_config['VCN']['subnet1']).data)
            self.subnets.append(self.client.get_subnet(instance_config['VCN']['subnet2']).data)
            self.subnets.append(self.client.get_subnet(instance_config['VCN']['subnet3']).data)

    def create_vcn(self):
        print('Creating VCN ...')
        vcn_details = CreateVcnDetails(
            cidr_block = self.config['vcn_cidr'],
            compartment_id = self.config['compartment'],
            display_name = self.config['display_name']
        )
        self.vcn_config = self.client.create_vcn(vcn_details).data

    def delete_vcn(self):
        while True:
            try: self.client.delete_vcn(self.vcn_id)   
            except Exception as e: continue
            break  

    def create_gateway(self):
        gateway_details = CreateInternetGatewayDetails(
            compartment_id = self.config['compartment'],
            is_enabled = True,
            vcn_id = self.vcn_config.id
        )
        self.gateway = self.client.create_internet_gateway(gateway_details).data

    def delete_internet_gateway(self):
        self.client.delete_internet_gateway(self.gateway_id)      

    def create_route_rules(self):
        route_rule = RouteRule(
            cidr_block = self.config['rt_cidr'],
            network_entity_id = self.gateway.id
        )
        self.route_rules.append(route_rule)
        route_table_details = UpdateRouteTableDetails(route_rules=self.route_rules)
        self.default_route_table = self.client.update_route_table(
            rt_id = self.vcn_config.default_route_table_id,
            update_route_table_details = route_table_details
        )
    
    def delete_route_rules(self):
        route_table_details = UpdateRouteTableDetails(route_rules=[])
        self.default_route_table = self.client.update_route_table(
            rt_id = self.rt_id,
            update_route_table_details = route_table_details
        )

    def create_subnets(self):
        for i, ad in enumerate(['ad_1', 'ad_2', 'ad_3']):
            subnet_details = CreateSubnetDetails(
                availability_domain = self.config[ad],
                cidr_block = '10.0.'+str(i)+'.0/24',
                compartment_id = self.config['compartment'],
                vcn_id = self.vcn_config.id
            )
            self.subnets.append(self.client.create_subnet(subnet_details).data)

    def delete_subnets(self):
        print('Terminating VCN ...\n')
        for subnet in self.subnets:
            while True:
                try: self.client.delete_subnet(subnet.id)
                except Exception as e: continue
                break

    def create_security_rules(self):
        security_list = self.client.get_security_list(security_list_id=self.vcn_config.default_security_list_id).data
        self.ingress_rules = security_list.ingress_security_rules
        self.egress_rules = security_list.egress_security_rules
        dest_port_range = PortRange(min=8000, max=8999)
        tcp_options = TcpOptions(destination_port_range=dest_port_range)
        security_rule = IngressSecurityRule(
            protocol = '6',
            source = '0.0.0.0/0',
            tcp_options = tcp_options
        )
        self.ingress_rules.append(security_rule)
        security_list_details = UpdateSecurityListDetails(
            ingress_security_rules=self.ingress_rules,
            egress_security_rules=self.egress_rules
        )
        self.default_security_list = self.client.update_security_list(
            security_list_id = self.vcn_config.default_security_list_id,
            update_security_list_details = security_list_details
        )

    def create_instance_config(self):
        config = ConfigParser()
        config['VCN'] = {
            'vcn_id': self.vcn_config.id,
            'gateway_id': self.gateway.id,
            'rt_id': self.vcn_config.default_route_table_id,
            'subnet1': self.subnets[0].id,
            'subnet2': self.subnets[1].id,
            'subnet3': self.subnets[2].id
        }
        with open('instance_config', 'w') as configfile:
            config.write(configfile)