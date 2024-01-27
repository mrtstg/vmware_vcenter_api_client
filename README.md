# vmware_vcenter_api_client

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

VMware vcenter client in httpx python library. Can be used for creating scripts for simple VM actions, like power control,
snapshot management etc.

Uses [VCenter REST API](https://developer.vmware.com/apis/vsphere-automation/latest/vcenter/) and VCenter SOAP API.

# Installation

If you use pip:

```bash
pip install git+https://github.com/mrtstg/vmware_vcenter_api_client
```

If you use poetry:

```bash
poetry add git+https://github.com/mrtstg/vmware_vcenter_api_client
```

# Usage

Client getting authenticated using user credentials that are getting passed into class.

```python
from vmware_vcenter_api_client.client import ApiClient, VM, Folder

# Protocol in the beginning of URL is nececcary
client = ApiClient("https://your.vcenter.server", "Administrator@vmware.server", "P@ssw0rd", False) # False disable SSL check

print(client.list_folders()) # list folders in the root
vmfolder = client.list_folders()[0]

vms = client.list_vm(folders=[vmfolder]) # list vms
client.start_vm(vms[0]) # start vm
```

# License

Code is under BSD3 license. See [LICENSE file](./LICENSE) for details.
