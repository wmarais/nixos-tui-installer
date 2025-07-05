import yaml
import subprocess
from dataclasses import dataclass, asdict
from typing import Self
from enum import Enum


class FileSystem(Enum):
    EFI: str = "efi"
    ZFS: str = "zfs"
    SWAP: str = "swap"
    RAW: str = "raw"

class PartitionTable(Enum):
    GPT: str = "gpt"

class Role(Enum):
    SERVER:  str = "server"
    DESKTOP: str = "desktop"
    LAPTOP:  str = "laptop"
    GAMING:  str = "gaming"
    SWENG:   str = "sweng"

@dataclass
class MountPoint:
    path: str
    options: list[str]

@dataclass
class Partition:
    label: str
    size: str
    file_system: FileSystem
    bootable: bool
    mount_point: MountPoint

@dataclass
class Device:
    path: str
    partition_table: PartitionTable
    partitions: list[Partition]

@dataclass
class Dataset:
    name: str
    mount_point: MountPoint

@dataclass
class Pool:
    name: str
    devices: list[str]
    data_sets: list[Dataset]

@dataclass
class ZFS:
    pools: list[Pool]

@dataclass
class Storage:
    name: str
    description: str
    devices: list[Device]
    zfs: ZFS

@dataclass
class Firewall:
    enable: bool = True
    allow_ping: bool = True
    allow_ssh: bool = True

@dataclass
class Network:
    hostname: str
    hostid: str
    ipv4_addrs: list[str] = None
    ipv6_addrs: list[str] = None
    domain: str = ""
    enable_dhcp: bool = True
    enable_ipv6: bool = False
    enable_doh: bool = True
    firewall: Firewall = Firewall()

@dataclass
class NixStore:
    allow_unfree: bool = True
    auto_upgrade: bool = True
    auto_clean: bool = True
    auto_optimise: bool = True

@dataclass
class Host:
    time_zone: str = ""
    locale: str = ""
    key_map: str = ""
    roles: list[Role] = []

@dataclass
class Configuration:
    hostname: str
    storage: Storage
    network: Network

    def save(self, file: str):
        with open(file, "w") as file:
            yaml.dump(asdict(self), file)

    def load(file: str) -> Self:
        with open(file, "r") as file:
            data = yaml.safe_load(file)
            return Configuration(**data)

# Add the custom representers for dumping the enum class' to yaml.
def file_system_enum_representer(dumper: yaml.dumper.Dumper, data: FileSystem):
    return dumper.represent_str(data.value)

def partition_table_enum_representer(dumper: yaml.dumper.Dumper, data: PartitionTable):
    return dumper.represent_str(data.value)

def role_enum_representer(dumper: yaml.dumper.Dumper, data: Role):
    return dumper.represent_str(data.value)

yaml.add_representer(FileSystem, file_system_enum_representer)
yaml.add_representer(PartitionTable, partition_table_enum_representer)
yaml.add_representer(Role, role_enum_representer)

if __name__ == "__main__":
    # Configure an example disk lay-out.
    device = Device("/dev/sda", PartitionTable.GPT, [
        Partition("boot", "1GiB", FileSystem.EFI, True, MountPoint("/boot", [])),
        Partition("swap", "4GiB", FileSystem.SWAP, False, None),
        Partition("zfsp", "100%", FileSystem.RAW, False, None)
    ])

    # Configure an example zfs layout.
    zfs = ZFS([
        Pool("zpool", [device.path], [
            Dataset("root", MountPoint("/", [])),
            Dataset("mnt", MountPoint("/mnt", [])),
            Dataset("var", MountPoint("/var", [])),
            Dataset("nix", MountPoint("/nix", [])),
            Dataset("home", MountPoint("/home", ["nodev"])),
            Dataset("tmp", MountPoint("/tmp", ["nodev", "nosuid", "noexec"]))
        ])
    ])

    # Setup the example storage configuration.
    storage = Storage("single_disk_zfs_root", "A single disk structure with a ZFS root.", 
                      [device], zfs)

    config = Configuration("mfpc01", storage)

    config.save("config.yml")
    config = Configuration.load("config.yml")