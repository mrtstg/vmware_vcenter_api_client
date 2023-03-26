import ssl
import httpx
import base64
from .structs.vm import VM
from .structs.folder import Folder
from pyVim.connect import SmartConnect, Disconnect, vim
from pyVim.task import WaitForTasks, WaitForTask


class ApiClient:
    session: httpx.Client
    login: str
    password: str
    session_id: str

    @staticmethod
    def _generate_httpx_client(
        base_url: str, verify: bool = True, **kwargs
    ) -> httpx.Client:
        return httpx.Client(base_url=base_url, verify=verify, timeout=15, **kwargs)

    def _authenticate(self):
        token = base64.b64encode(
            f"{self.login}:{self.password}".encode("ascii")
        ).decode("ascii")
        response = self.session.post(
            "api/session", headers={"Authorization": f"Basic {token}"}
        )
        response.raise_for_status()
        self.session_id = response.json()
        self.session.headers = {"vmware-api-session-id": self.session_id}

    def _get_vim_vm_by_bios_uuid(self, uuid: str) -> vim.VirtualMachine | None:
        return self.sdk_client.RetrieveContent().searchIndex.FindByUuid(
            uuid=uuid, vmSearch=True
        )

    def create_vms_snapshot(
        self,
        vms: list[VM],
        name: str,
        description: str,
        dump_memory: bool = True,
        quiesce: bool = False,
    ) -> dict[str, bool]:
        tasks = []
        stats = {}
        for vm in vms:
            stats[vm.vm] = False

            vm_info = self.get_vm_info(vm)
            bios_uuid: str = vm_info["identity"]["bios_uuid"]
            vim_vm = self._get_vim_vm_by_bios_uuid(bios_uuid)
            if vim_vm is None:
                continue

            tasks.append(vim_vm.CreateSnapshot(name, description, dump_memory, quiesce))
            stats[vm.vm] = True

        WaitForTasks(tasks)
        return stats

    def _lookup_snapshots(self, snapshots, filter_l: bool = True) -> list:
        res = []
        for snapshot in snapshots:
            if not isinstance(snapshot, list):
                res.append(snapshot)
            if snapshot.childSnapshotList is not None and snapshot.childSnapshotList:  # type: ignore
                res.extend(self._lookup_snapshots(snapshot.childSnapshotList, False))  # type: ignore

        if filter_l:
            f_res = []
            for i in res:
                if i == []:
                    continue
                if isinstance(i, list):
                    f_res.extend(i)
                else:
                    f_res.append(i)
            return f_res
        return res

    def revert_vms_to_snapshot(self, vms: list[VM], name: str) -> dict[str, bool]:
        tasks = []
        stats = {}
        for vm in vms:
            stats[vm.vm] = False

            vm_info = self.get_vm_info(vm)
            bios_uuid: str = vm_info["identity"]["bios_uuid"]
            vim_vm = self._get_vim_vm_by_bios_uuid(bios_uuid)
            if vim_vm is None:
                continue

            for snapshot in self._lookup_snapshots(vim_vm.snapshot.rootSnapshotList):
                if snapshot.name == name:
                    tasks.append(snapshot.snapshot.RevertToSnapshot_Task())
                    stats[vm.vm] = True
                    break
        WaitForTasks(tasks)
        return stats

    def delete_vms_snapshot(self, vms: list[VM], name: str) -> dict[str, bool]:
        tasks = []
        stats = {}
        for vm in vms:
            stats[vm.vm] = False

            vm_info = self.get_vm_info(vm)
            bios_uuid: str = vm_info["identity"]["bios_uuid"]
            vim_vm = self._get_vim_vm_by_bios_uuid(bios_uuid)
            if vim_vm is None:
                continue

            if vim_vm.snapshot is None:
                continue

            for snapshot in self._lookup_snapshots(vim_vm.snapshot.rootSnapshotList):
                if snapshot.name == name:
                    tasks.append(snapshot.snapshot.RemoveSnapshot_Task(False))
                    stats[vm.vm] = True
                    break

        WaitForTasks(tasks)
        return stats

    def list_folders(
        self, folders: list[Folder] = [], parent_folders: list[Folder] = []
    ) -> list[Folder]:
        response = self.session.get(
            "api/vcenter/folder",
            params={
                "folders": [f.folder for f in folders],
                "parent_folders": [f.folder for f in parent_folders],
            },
        )
        response_list = []
        response.raise_for_status()
        for folder in response.json():
            response_list.append(Folder(folder))
        return response_list

    def get_vm_info(self, vm: VM) -> dict:
        response = self.session.get("api/vcenter/vm/%s" % vm.vm)
        response.raise_for_status()
        return response.json()

    def _perform_vm_power_action(self, vm: VM, action: str) -> bool:
        return (
            self.session.post(
                "api/vcenter/vm/%s/power" % vm.vm, params={"action": action}
            ).status_code
            == 204
        )

    def reboot_vm(self, vm: VM) -> bool:
        return self._perform_vm_power_action(vm, "reset")

    def start_vm(self, vm: VM) -> bool:
        return self._perform_vm_power_action(vm, "start")

    def stop_vm(self, vm: VM) -> bool:
        return self._perform_vm_power_action(vm, "stop")

    def list_vm(
        self,
        folders: list[Folder] = [],
    ) -> list[VM]:
        response = self.session.get(
            "api/vcenter/vm",
            params={
                "folders": [f.folder for f in folders],
            },
        )
        response_list = []
        response.raise_for_status()
        for vm in response.json():
            response_list.append(VM(vm))
        return response_list

    def __init__(self, host: str, login: str, password: str, verify: bool = True):
        self.session = self._generate_httpx_client(host, verify)
        self.sdk_client = SmartConnect(
            host=host[host.find("//") + 2 :],
            user=login,
            pwd=password,
            sslContext=ssl.SSLContext(ssl.PROTOCOL_TLS),
        )
        self.login = login
        self.password = password
        self._authenticate()
