import logging

from ..util import net_util
from ..compute import DockerCompute
from cattle.agent.handler import BaseHandler

log = logging.getLogger('docker')


class NetworkSetup(BaseHandler):
    def __init__(self):
        self.compute = DockerCompute()
        pass

    def before_start(self, instance, host, config, start_config):
        mac_address = None
        device_number = None
        for nic in instance.nics:
            if device_number is None:
                mac_address = nic.macAddress
                device_number = nic.deviceNumber
            elif device_number > nic.deviceNumber:
                mac_address = nic.macAddress
                device_number = nic.deviceNumber
        config["mac_address"] = mac_address

    def after_start(self, instance, host, id):
        try:
            for nic in instance.nics:
                ip_address = None

                for ip in nic.ipAddresses:
                    if ip.role == 'primary':
                        ip_address = '{0}/{1}'.format(ip.address,
                                                      ip.subnet.cidrSize)

                if ip_address is None:
                    continue

                inspect = self.compute.inspect(id)
                pid = inspect['State']['Pid']

                net_util(pid, ip=ip_address,
                         device='eth{0}'.format(nic.deviceNumber))
        except (KeyError, AttributeError):
            pass
