from pydantic import BaseModel, Field

class Flavor(BaseModel):
    """
        Describes the availability of a flavor with the most essential information.
    """
    id: str  = Field(..., description= "Openstack Id")
    name: str  = Field(..., description= "human readable name of the flavor")
    available: int  = Field(..., description = "currently available flavors (positive integer)")
    total: int = Field(..., description = "total available flavors (postive integer)")

class ExtendedFlavor(Flavor):
    """
        Contains extended cloud flavor information based on Legacy L
    """
    cores: int = Field(..., description="Number of virtual cores.")
    mem: int = Field(..., description="Memory size in MB.")
    type: str = Field(..., description="Flavor type. One of 'DEFAULT', 'GPU', 'HIGHMEM'")
    gpu_type: str = Field(..., description="GPU type. For example Nvidia T4, L4, A40, A100, H100, ...")
    gpu_count: int = Field(..., description="Number of GPUs.")
    root_disk: int = Field(..., description="Root disk size in GB.")
    ephemeral_disk: int = Field(..., description="Ephemeral disk size in GB.")
