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

    def __init__(self, config):
        self.config = config
        self.client = VirtualNetworkClient(config)
        self.subnets = []
        self.route_rules = []
        self.security_rules = []

    def create_vcn(self):
        print 'Creating VCN ...' 
        vcn_details = CreateVcnDetails(
            cidr_block = self.config['vcn_cidr'],
            compartment_id = self.config['compartment'],
            display_name = self.config['display_name']
        )
        self.vcn_config = self.client.create_vcn(vcn_details).data

    def create_gateway(self):
        gateway_details = CreateInternetGatewayDetails(
            compartment_id = self.config['compartment'],
            is_enabled = True,
            vcn_id = self.vcn_config.id
        )
        self.gateway = self.client.create_internet_gateway(gateway_details).data

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

    def create_subnet(self, ad):
        cidr = '10.0.'+str(int(ad[-1])-1)+'.0/24'
        print 'Creating subnet with cidr: %s' % (cidr)
        subnet_details = CreateSubnetDetails(
            availability_domain = self.config[ad],
            cidr_block = cidr,
            compartment_id = self.config['compartment'],
            vcn_id = self.vcn_config.id
        )
        try: 
            self.subnets.append(self.client.create_subnet(subnet_details).data)
        except Exception as e:
            pass
        finally:
            pass
        while True:
            try:
                subnet = self.client.get_subnet(subnet_id=self.subnets[-1].id).data
                if subnet.lifecycle_state == 'AVAILABLE':
                    return
                else: 
                    continue
            except Exception as e:
                continue
            finally:
                return


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