import yaml
from dataclasses import dataclass, asdict
from typing import Self
from enum import Enum

class FileSystem(Enum):
    BTRFS:      str = "btrfs"
    EXT2:       str = "ext2"
    EXT3:       str = "ext3"
    EXT4:       str = "ext4"
    FAT16:      str = "fat16"
    FAT32:      str = "fat32"
    HFS:        str = "hfs"
    HFSP:       str = "hfs+"
    SWAP:       str = "linux-swap"
    NTFS:       str = "ntfs"
    REISERFS:   str = "reiserfs"
    UDF:        str = "udf"
    XFS:        str = "xfs"
    NONE:       str = ""

class PartitionTable(Enum):
    AIX:        str = "aix"
    AMIGA:      str = "amiga"
    BSD:        str = "bsd"
    DVH:        str = "dvh"
    GPT:        str = "gpt"
    LOOP:       str = "loop"
    MAC:        str = "mac"
    MSDOS:      str = "msdos"
    PC98:       str = "pc98"
    SUN:        str = "sun"

class PartitionFlags(Enum):
    BOOT:               str = "boot"
    ROOT:               str = "root"
    SWAP:               str = "swap"
    HIDDEN:             str = "hidden"
    RAID:               str = "raid"
    LVM:                str = "lvm"
    LBA:                str = "lba"
    LEGACY_BOOT:        str = "legacy_boot"
    IRST:               str = "irst"
    MSFTRES:            str = "msftres"
    ESP:                str = "esp"
    CHROMEOS_KERNEL:    str = "chromeos_kernel"
    BLS_BOOT:           str = "bls_boot"
    LINUX_HOME:         str = "linux_home"
    NO_AUTOMOUNT:       str = "no_automount"
    BIOS_GRUB:          str = "bios_grub"
    PALO:               str = "palo"

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
    start: str
    end: str
    file_system: FileSystem
    bootable: bool
    mount_point: MountPoint
    flags: list[PartitionFlags]
    index: int = -1

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
    firewall: Firewall = None

@dataclass
class NixStore:
    allow_unfree: bool = True
    auto_upgrade: bool = True
    auto_clean: bool = True
    auto_optimise: bool = True

@dataclass
class Host:
    time_zone: str
    locale: str
    key_map: str
    roles: list[Role]

@dataclass
class Configuration:
    name: str
    descritpion: str
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

def partition_flags_enum_representer(dumper: yaml.dumper.Dumper, data: PartitionFlags):
    return dumper.represent_str(data.value)

yaml.add_representer(FileSystem, file_system_enum_representer)
yaml.add_representer(PartitionTable, partition_table_enum_representer)
yaml.add_representer(PartitionFlags, partition_flags_enum_representer)
yaml.add_representer(Role, role_enum_representer)

if __name__ == "__main__":
    # Configure an example disk lay-out.
    device = Device("/dev/sda", PartitionTable.GPT, [
        Partition("boot", "1MiB", "1GiB", FileSystem.FAT32, True, MountPoint("/boot", []), [PartitionFlags.ESP]),
        Partition("swap", "1GiB", "5GiB", FileSystem.SWAP, False, None, [PartitionFlags.SWAP]),
        Partition("zfsd", "5GiB", "100%", FileSystem.NONE, False, None, [])
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
    
    network = Network("mypc01", "12345678", ["192.168.1.1/24"])

    config = Configuration("single_disk_zfs_root", "Setting up NixOS on a single Disk, using a \
ZFS root file system.", storage, network)

    config.save("config.yml")
    config = Configuration.load("config.yml")