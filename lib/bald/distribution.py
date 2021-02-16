from enum import Enum
"""
Adds an Enum for MIME_TYPE and LINKED_DATA_RESOURCE_DEFINING_NETCDF for use
  in Schema.org and DCAT outputs
"""
class BaldDistributionEnum(Enum):
    MIME_TYPE = "application/x-netcdf"
    LINKED_DATA_RESOURCE_DEFINING_NETCDF = "http://vocab.nerc.ac.uk/collection/M01/current/NC/"