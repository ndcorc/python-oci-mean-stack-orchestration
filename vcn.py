
class VCN(Orchestration):

    def __init__(self):
        self.client = oci.core.virtual_network_client.VirtualNetworkClient(config)
        self.compartment = None
        self.ADs = None
        self.display_name = None
        #self.images = compute.list_images(config['eastgroup']).data
        self.compartment = None
        self.subnets = []
        self.gateways = []
        self.route_tables = []
        self.security_lists = []

    def select_compartment(self):
        print('Create in Compartment: \n')
        for index, compartment in enumerate(Orchestration.compartments):
            print(compartment.name + ' - (' + str(index+1) + ')')
        choice = input('\nChoice: ')
        self.compartment = Orchestration.compartments[int(choice)-1]
        self.ADs = Orchestration.identity.list_availability_domains(self.compartment).data

    #def define_cidr_block(self):

    def create_gateway(self):
        gateway_details = oci.core.model.create_internet_gateway_details.CreateInternetGatewayDetails(
            compartment_id=self.compartment.compartment_id
        )
        self.gateways.append(gateway)
        self.route_tables.append(self.create_route_table())
        self.subnets.append(self.create_subnet())
        self.security_lists.append(self.create_security_list())

    def create_route_table(self):
        return None

    def create_subnet(self):
        return None

    def create_security_list(self):
        return None

    def create_vcn(self):
        print('Creating VCN ...\n')
        self.select_compartment()
        self.display_name = input('Display Name: ')
        #self.cidr_block = self.define_cidr_block()
        vcn_details = oci.core.models.create_vcn_details.CreateVcnDetails(
            cidr_block='10.0.0.0/16',
            compartment_id=compartment.id,
            display_name=display_name
        )
        self.vcn = self.client.create_vcn(vcn_details)