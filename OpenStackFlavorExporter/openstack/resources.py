""" Module contains classes  Resources and ResourcesException."""
import OpenStackFlavorExporter.openstack

from OpenStackFlavorExporter.model import ExtendedFlavor

import sys



class Resources: # pylint: disable=too-many-instance-attributes
    """
    Generates a data structure containing all hypervisors with available resources.
    Additional the count of all possible flavor can be calculated.
    """

    def __init__(self, cpu_overprovisioning=4):
        self.__osclient__ = OpenStackFlavorExporter.openstack.create_osclient()

        self.__hypervisors__ = {}
        self.__gpu_instances_by_host__ = {}

        self.__map_of_aggregates__ = {}
        self.__map_of_hypervisors__ = {}
        self.__flavors__:list[ExtendedFlavor]  = []

        self.cpu_overprovisioning = cpu_overprovisioning


    def __getV(self, map,key,default=None):
        ''' Helper function that return value from map['key'] if set, default otherwise '''
        if key in map:
            return map[key]
        return default
    
    def __update_gpu_instances_by_host__(self):
        """
        Helper method. Update map of gpu instances by host.
        """
        for instance in self.__osclient__.list_servers(all_projects=True):
            # Filter all GPU instances
            if "pci_passthrough:alias" in instance["flavor"]["extra_specs"].keys():
                if instance["OS-EXT-SRV-ATTR:host"] not in self.__gpu_instances_by_host__:
                    self.__gpu_instances_by_host__[instance["OS-EXT-SRV-ATTR:host"]] = []
                self.__gpu_instances_by_host__[instance["OS-EXT-SRV-ATTR:host"]].append(instance)

    def __update_aggregates__(self):
        """
        Collect information about used and available resources and update internal data structure.
        """

        result = {}

        # create a map of hypervisor to make life a bit easier 
        for hypervisor in self.__osclient__.list_hypervisors():
            self.__hypervisors__[hypervisor["name"].split('.')[0]] = hypervisor

        
        for aggregate in self.__osclient__.list_aggregates():

            # collect all hypervisor of this aggregate
            hypervisors = []
            for hostname in aggregate["hosts"]:

                # determine number of used gpus
                gpu_used = 0
                
                if hostname in self.__gpu_instances_by_host__:
                    for instance in self.__gpu_instances_by_host__[hostname]:
                        gpu_used = gpu_used + int(instance["flavor"]["extra_specs"]["pci_passthrough:alias"].split(":")[1])

                hypervisor = self.__hypervisors__[hostname]

                hypervisors.append({"name": hypervisor["name"].split('.')[0],
                                        "status": hypervisor["status"],
                                        "state": hypervisor["state"],
                                        "running_vms": int(hypervisor['running_vms']),
                                        "gpu": bool(self.__getV(aggregate["metadata"], 'gpu', False)),
                                        "gpus": int(self.__getV(aggregate["metadata"], 'gpu_count', 0)), # type: ignore
                                        "gpu_type": self.__getV(aggregate["metadata"], "gpu_type", 'none'),
                                        "gpus_used": int(gpu_used),
                                        "vcpus": int(hypervisor["vcpus"]),
                                        "vcpus_used": int(hypervisor["vcpus_used"]),
                                        "memory": int(hypervisor["memory_size"]),               # in MB
                                        "memory_free": int(hypervisor["memory_free"]),          # in MB
                                        "disk": int(hypervisor["local_disk_size"]),             # in GB
                                        "disk_available": int(hypervisor["disk_available"]),    # in GB
                                        })

            # add necessary aggregate information to datastructure
            result[aggregate["name"]] = {}
            result[aggregate["name"]]["gpu"] = self.__getV(aggregate["metadata"], 'gpu', False)
            result[aggregate["name"]]["gpu_type"] = self.__getV(aggregate["metadata"], "gpu_type", 'none')
            result[aggregate["name"]]["gpu_count"] = int(self.__getV(aggregate["metadata"], 'gpu_count', 0)) # type: ignore
            result[aggregate["name"]]["hypervisors"] = hypervisors

        self.__map_of_aggregates__ = result

    def __update_flavors__(self):
        """
        Internal helper functions, that calculates available and total number of flavors.
        """

        flavors =  []

        for flavor in self.__osclient__.list_flavors(): # pylint: disable=too-many-nested-blocks

            # ignore all disabled and flavors with a name containing substring "DEPRECATED"
            if flavor["is_disabled"] != "false" and flavor["name"].find("DEPRECATED") == -1:
                total = 0
                available = 0
                # sum up all local disk space disk and ephemeral are measured in GB, swap in MB
                local_disk = flavor["disk"] + flavor["ephemeral"]
                if flavor["swap"] > 0:
                    local_disk += int(flavor["swap"] / 1024)

                # get gpu type and count if flavor has  GPU(s) specified
                gpu_type = ''
                gpu_count= 0
                flavor_type = "default"
                if "pci_passthrough:alias" in flavor["extra_specs"].keys():
                    gpu_type, gpu_count = flavor["extra_specs"]["pci_passthrough:alias"].split(":")
                    flavor_type = "gpu"
                

                # iterate over all aggregates
                for aggegrate in self.__map_of_aggregates__.values():

                    # iterate over all hypervisor of current aggregate
                    for hypervisor in aggegrate["hypervisors"]:
                        # skip disabled and down hypervisor
                        if hypervisor["status"] == "disabled" or hypervisor["state"] == "down":
                            continue

                        # if current flavor addresses a GPU ...
                        if flavor_type == "gpu":
                            # ... calculate the availibility of total and current GPUs.
                            if aggegrate["gpu_type"] == gpu_type:
                                t_gpu = int(hypervisor["gpus"] / int(gpu_count))
                                c_gpu = max(0,int((hypervisor["gpus"] - hypervisor["gpus_used"]) / int(gpu_count)))
                            else:
                                t_gpu = 0
                                c_gpu = 0
                        else:
                            # ignore t_gpu and c_gpu for non GPU flavors ...
                            t_gpu = sys.maxsize
                            c_gpu = sys.maxsize
                            
                        # calculate availability of total and current general resources 
                        t_vcpu = int(
                            int(hypervisor["vcpus"]) * self.cpu_overprovisioning / int(flavor["vcpus"]))
                        t_mem = int(int(hypervisor["memory"]) / int(flavor["ram"]))
                        t_disk = int(int(hypervisor["disk"] / local_disk))
                                  
                        c_vcpu = max(0,int((int(hypervisor["vcpus"]) * self.cpu_overprovisioning - int(
                            hypervisor["vcpus_used"])) / int(flavor["vcpus"])))
                        c_mem = max(0,int(int(hypervisor["memory_free"]) / int(flavor["ram"])))
                        c_disk = max(0,int(int(hypervisor["disk_available"] / local_disk)))
                        
                        # add minimum of all resources needed to total number
                        total += min(t_gpu, t_vcpu, t_mem, t_disk)
                        # add minimum of current available resources 
                        available += min(c_gpu, c_vcpu, c_mem, c_disk)


                # Append flavor
                flavors.append(ExtendedFlavor(
                                name=flavor["name"],
                                id=flavor["id"],
                                available=available,
                                total=total,
                                type=flavor_type,
                                cores=flavor["vcpus"],
                                mem = flavor["ram"],
                                gpu_type=gpu_type,
                                gpu_count=gpu_count,
                                root_disk=flavor["disk"],
                                ephemeral_disk=flavor["ephemeral"]))
                
            self.__flavors__ = flavors

    def update(self):
        """
        Update internal datastructures, calculates the number of total and available flavors.
        """
        # The following call is very time-consuming but necessary as long as no Unified Resources are used.
        self.__update_gpu_instances_by_host__()
        self.__update_aggregates__()
        self.__update_flavors__()

    def getFlavors(self):
        """
        Return a possible empty list of Flavor objects.

        :return: List of Flavor objects
        """
        return self.__flavors__

    def getFlavor(self, flavorid):
        """
        Return Flavor with given id. Raise exception in case of non existing id.

        :param flavorid: id of flavor
        :return: Flavor object with given id
        """
        for flavor in self.__flavors__:
            if flavor.id == flavorid:
                return flavor
        raise ResourceException("Unknown flavor id!")


class ResourceException(Exception):
    """ ResourceException to avoid throwing a general exception."""

    def __init__(self, msg):
        super().__init__(f"Resource: {msg}")
