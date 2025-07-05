#! /usr/bin/env python3

import argparse

import os
import subprocess
from src.configuration import *

def check_error(func):
    result = func()
    if result.returncode != 0:
        raise Exception(result.stderr)

def setup_partitions(devices: list[Device]):
    for device in devices:
        subprocess.call(["parted", "-s", device.path, "mklabel", device.partition_table.value])

        index = 1
        for partition in device.partitions:
            check_error(subprocess.call(["parted", "-s", "-a", "optimal", device.path, "mkpart", 
                partition.label, partition.file_system.value, partition.start, partition.end]))
            
            for flag in partition.flags:
                check_error(subprocess.call(["parted", "-s", device.path, "set", index, 
                    flag.value, "on"]))

            index = index + 1

parser = argparse.ArgumentParser(description="A command line tool to configure a NixOS host. It "\
                                 "attempts to compliment NixOS's build reproducibility by " \
                                 "providing a means to configuration manage the host installation.")

parser.add_argument('-s', '--save', type=str,
                    help="The directory to save the installer configuration too. The contents of "\
                    "of this directory can be configuration managed for future rebuilds.")

parser.add_argument('-l', '--load', type=str,
                    help="The directory containing a previously saved configuration to load.")

parser.add_argument('-r', '--run', action='store_true',
                    help="Execute the build configuration loaded using -l or --load. Use this to "\
                    "build to configuration managed base-line.")

parser.add_argument('-e', '--exact', action='store_true',
                    help="Prevent the installer from adjusting the host specific properties such "\
                    "as Host ID, GPU Driver, CPU, etc. Run this when rebuilding a replacing a "\
                    "failed host")

args = parser.parse_args()


config: Configuration = None

# Check if the user want to load an existing configuration.
if args.load:
    print(f"Loading: {args.load}/config.yml")
    config = Configuration.load(f"{args.load}/config.yml")

# Check if the user want to run the automatic installer.
if args.run:
    setup_partitions(config.storage.devices)

# Check if the user want to save the configuration.
if args.save:
    print(f"Saving Configuration: {args.save}/config.yml")
    if not os.path.exists(args.save):
        os.makedirs(args.save)
    config.save(f"{args.save}/config.yml")



