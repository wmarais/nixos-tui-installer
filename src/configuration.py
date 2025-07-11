from dataclasses import dataclass, asdict
from dataclass_wizard import YAMLWizard
from typing import Self
from enum import Enum
from typing import List

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

    def __getitem__(self, name) -> str:
        return self.value

    def startswith(self, value) -> bool:
        return self.value.startswith(value)

    def __len__(self):
        return len(self.value)


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

    def __getitem__(self, name) -> str:
        return self.value

    def startswith(self, value) -> bool:
        return self.value.startswith(value)

    def __len__(self):
        return len(self.value)

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

    def __getitem__(self, name) -> str:
        return self.value

    def startswith(self, value) -> bool:
        return self.value.startswith(value)

    def __len__(self):
        return len(self.value)

class Role(Enum):
    SERVER:  str = "server"
    DESKTOP: str = "desktop"
    LAPTOP:  str = "laptop"
    GAMING:  str = "gaming"
    SWENG:   str = "sweng"

    def __getitem__(self, name) -> str:
        return self.value

    def startswith(self, value) -> bool:
        return self.value.startswith(value)

    def __len__(self):
        return len(self.value)

@dataclass
class MountPoint(YAMLWizard):
    path: str
    options: List[str]

@dataclass
class Partition(YAMLWizard):
    label: str
    start: str
    end: str
    file_system: FileSystem
    bootable: bool
    mount_point: MountPoint | None = None
    flags: List[PartitionFlags] | None = None
    index: int = -1

@dataclass
class Device(YAMLWizard):
    path: str
    partition_table: PartitionTable
    partitions: List[Partition] | None = None

@dataclass
class Dataset(YAMLWizard):
    name: str
    mount_point: MountPoint | None = None

@dataclass
class Pool(YAMLWizard):
    name: str
    devices: List[str]
    data_sets: List[Dataset]

@dataclass
class ZFS(YAMLWizard):
    pools: List[Pool]

@dataclass
class Storage(YAMLWizard):
    name: str
    description: str
    devices: List[Device]
    zfs: ZFS

@dataclass
class Firewall(YAMLWizard):
    enable: bool
    allow_ping: bool
    allow_ssh: bool

@dataclass
class Network(YAMLWizard):
    hostname: str
    hostid: str
    ipv4_addrs: List[str]
    ipv6_addrs: List[str]
    domain: str
    enable_dhcp: bool
    enable_ipv6: bool
    enable_doh: bool
    firewall: Firewall

@dataclass
class NixStore(YAMLWizard):
    allow_unfree: bool
    auto_upgrade: bool
    auto_clean: bool
    auto_optimise: bool

@dataclass
class Host(YAMLWizard):
    time_zone: str
    locale: str
    key_map: str
    roles: List[Role]

@dataclass
class Configuration(YAMLWizard):
    name: str
    descritpion: str
    storage: Storage
    network: Network

    def save(self, file: str):
        self.to_yaml_file(file)

    def load(file: str) -> Self:
        return Configuration.from_yaml_file(file)

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

    network = Network("mypc01", "12345678", ["192.168.1.1/24"], [], "", False, False, True,
                      Firewall(True, True, True))


    config = Configuration("single_disk_zfs_root", "Setting up NixOS on a single Disk, using a \
ZFS root file system.", storage, network)

    config.save("config.yml")
    config = Configuration.load("config.yml")

    print(config.storage.devices)