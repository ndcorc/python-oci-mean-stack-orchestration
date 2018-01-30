

class Compute(Orchestration):

    def __init__(self, config):
        self.client = oci.core.compute_client.ComputeClient(config)
        self.images = client.list_images(config['eastgroup']).data
        self.identity = oci.identity.identity_client.IdentityClient(config)
        self.ADs = self.identity.list_availability_domains(config['eastgroup']).data

    def select_AD(self):
        print('Select an Availability Domain:\n')
        for index, AD in enumerate(ADs):
            print(AD.name + ' - (' + str(index+1) + ')')
        choice = input('\nChoice: ')
        return ADs[int(choice)-1].name

    def select_image_os(self):
        print('\n\nSelect an Image Operating System:\n')
        operating_systems = {}
        for im in images:
            os = im.operating_system + " " + im.operating_system_version
            if os not in operating_systems:
                operating_systems[os] = im.id
        os_keys = list(operating_systems.keys())
        for index, os in enumerate(os_keys):
            print(os + ' - (' + str(index+1) + ')')
        choice = input('\nChoice: ')
        image_os = os_keys[int(choice)-1]
        image_id = operating_systems[os_keys[int(choice)-1]]
        self.source_details = oci.core.models.instance_source_via_image_details.InstanceSourceViaImageDetails(image_id=image_id)
        return image_os, image_id

    def select_shape(self, image_id):
        print('\n\nSelect a Shape Type:\n\nVirtual Machine - (1)\nBare Metal Machine - (2)')
        choice = input('\nChoice: ')
        shape_type = 'VM' if int(choice) == 1 else 'BM'
        shapes = compute.list_shapes(config['eastgroup'], image_id=image_id).data
        shapes = [shape for shape in shapes if shape.shape.startswith(shape_type)]
        for index, shape in enumerate(shapes):
            print(shape.shape + ' - (' + str(index+1) + ')')
        choice = input('\nChoice: ')
        return shapes[int(choice)-1].shape

    def create_vnic_details(self):
        print('\n\nSelect a Virtual Cloud Network:\n')
        vcn = select_vcn()
        print('\n\nSelect a Subnet:\n')
        subnet = select_subnet(vcn)
        vnic_details = oci.core.models.create_vnic_details.CreateVnicDetails(subnet_id=subnet)
        return vnic_details

    def create_metadata(self):
        ssh_key = input('\n\nPaste your public SSH key (in ssh-rsa format): ')
        user_data = input('\n\nPaste any user data for custom scripts: ')
        metadata = {
            'ssh_authorized_keys': ssh_key,
            'user_data': user_data
        }
        return metadata

    def launch_instance(self, subnets):
        print('Creating compute instance ...\n')
        availability_domain = select_AD()
        display_name = input('\nDisplay Name: ')
        image_os, image_id = select_image_os()
        shape = select_shape(image_id)
        vnic_details = self.create_vnic_details()
        metadata = create_metadata()
  
        compute_details = oci.core.models.launch_instance_details.LaunchInstanceDetails(
            availability_domain=availability_domain,
            compartment_id=compartment_id,
            image_id=image_id,
            shape=shape
        )
        compute_instance = compute.launch_instance(compute_details)