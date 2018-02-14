from configparser import RawConfigParser
import os, threading

import oci
from oci.core.compute_client import ComputeClient
from oci.core.models.launch_instance_details import LaunchInstanceDetails

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend


class Compute(object):

    def __init__(self, config, subnet):
        self.config = config
        self.client = ComputeClient(config)
        self.operating_systems = self.get_operating_systems()
        self.subnet = subnet
        self.keyfile = 'private'+self.subnet.availability_domain[-1]+'.pem'
        self.name = self.config['display_name']+' '+self.subnet.availability_domain[-1]

    def get_operating_systems(self):
        operating_systems = {}
        images = self.client.list_images(self.config['compartment']).data
        for image in images:
            os = image.operating_system + " " + image.operating_system_version
            if os not in operating_systems:
                operating_systems[os] = image.id
        return operating_systems

    def create_metadata(self):
        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048
        )
        self.private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.TraditionalOpenSSL,
            crypto_serialization.NoEncryption())
        self.public_key = key.public_key().public_bytes(
            crypto_serialization.Encoding.OpenSSH,
            crypto_serialization.PublicFormat.OpenSSH
        )
        with open('./'+self.keyfile, 'w+') as f:
            os.chmod('./'+self.keyfile, 0o600)
            f.write(self.private_key.decode())
        print 'Created private ssh key - "./'+self.keyfile+'"' 
        metadata = {
            'ssh_authorized_keys': self.public_key.decode()
        }
        return metadata

    def launch_instance(self):
        print 'Creating compute instance ...' 
        compute_details = LaunchInstanceDetails(
            availability_domain = self.subnet.availability_domain,
            compartment_id = self.config['compartment'],
            display_name = self.name,
            image_id = self.operating_systems[self.config['image_os']],
            shape = self.config['shape'],
            subnet_id = self.subnet.id,
            metadata = self.create_metadata()
        )
        while True:
            try:
                self.compute_instance = self.client.launch_instance(compute_details).data
                return
            except Exception as e:
                continue
        
    def get_vnic(self, vcn):
        while True:
            vnic_attachments = self.client.list_vnic_attachments(self.config['compartment']).data
            for attachment in vnic_attachments:
                if self.compute_instance.id == attachment.instance_id:
                    vnic = vcn.client.get_vnic(attachment.vnic_id).data
                    self.public_ip = vnic.public_ip
                    self.private_ip = vnic.private_ip
                    return

    def terminate_instance(self):
        print 'Terminating compute instance ...' 
        self.client.terminate_instance(self.instance_id)