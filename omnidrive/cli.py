#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 OMNIDRIVE CLI v1.0 [PREMIUM RELEASE]
Unified Virtual Disk Storage & Symlink Manager for the j1010red Ecosystem
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path

# Vibrant color codes to match the J Command Center aesthetic
C_MAGENTA = '\033[38;5;201m'
C_PINK = '\033[38;5;213m'
C_CYAN = '\033[38;5;51m'
C_GOLD = '\033[38;5;220m'
C_RED = '\033[38;5;196m'
C_GREEN = '\033[38;5;46m'
C_RESET = '\033[0m'
C_BOLD = '\033[1m'

DEFAULT_IMAGE_PATH = Path.home() / "OmniDrive_System" / "OmniDrive_Jack.sparsebundle.sparseimage"
DEFAULT_MOUNT_POINT = Path("/Volumes/OmniDrive")

# Pre-defined symlinks mapping in OmniDrive -> targets on the local system
DEFAULT_LINKS = {
    "Google Drive": Path.home() / "Library/CloudStorage/GoogleDrive-descartes131@gmail.com",
    "Macintosh HD (Local Mac)": Path("/"),
    "The Ark App": Path.home() / "RewardAggregatorApp",
    "The Ark Repo": Path.home() / "RewardAggregator",
    "iCloud Drive": Path.home() / "Library/Mobile Documents/com~apple~CloudDocs",
}

def header():
    print(f"{C_MAGENTA}{C_BOLD}✨ OMNIDRIVE CONTROL CENTER v1.0 [PUBLIC RELEASE] ✨{C_RESET}")
    print(f"{C_PINK}------------------------------------------------------------{C_RESET}")

def run_cmd(cmd, check=True, capture_output=True):
    try:
        res = subprocess.run(cmd, shell=True, check=check, text=True,
                             capture_output=capture_output)
        return res.stdout.strip() if res.stdout else ""
    except subprocess.CalledProcessError as e:
        if check:
            print(f"{C_RED}❌ Error running command:{C_RESET} {cmd}\n{e.stderr or e}")
            sys.exit(1)
        return ""

def is_mounted(mount_point=DEFAULT_MOUNT_POINT):
    out = run_cmd("mount", check=False)
    return str(mount_point) in out

def check_status():
    header()
    print(f"💾 {C_BOLD}MOUNT STATUS{C_RESET}")
    mounted = is_mounted()
    
    if mounted:
        print(f"  Mount Point: {C_GREEN}[ONLINE]{C_RESET} {DEFAULT_MOUNT_POINT}")
        # Get storage stats
        total, used, free = shutil.disk_usage(DEFAULT_MOUNT_POINT)
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        used_percent = (used / total) * 100
        
        print(f"  Capacity:    {C_GOLD}{total_gb:.2f} GB{C_RESET} total | {C_GOLD}{used_gb:.2f} GB{C_RESET} used | {C_GOLD}{free_gb:.2f} GB{C_RESET} free")
        print(f"  Usage:       {C_PINK}[{'#' * int(used_percent/5)}{'-' * (20 - int(used_percent/5))}] {used_percent:.1f}%{C_RESET}")
        
        # Verify symlinks
        print(f"\n🔗 {C_BOLD}UNIFIED SYMLINKS STATUS{C_RESET}")
        for link_name, target in DEFAULT_LINKS.items():
            link_path = DEFAULT_MOUNT_POINT / link_name
            if link_path.is_symlink():
                resolved = link_path.resolve()
                if resolved.exists():
                    print(f"  🟢 {C_PINK}{link_name:<25}{C_RESET} -> {resolved} {C_GREEN}(Valid){C_RESET}")
                else:
                    print(f"  🔴 {C_PINK}{link_name:<25}{C_RESET} -> {resolved} {C_RED}(Broken target){C_RESET}")
            else:
                if link_path.exists():
                    print(f"  ⚠️  {C_PINK}{link_name:<25}{C_RESET} exists but is not a symlink")
                else:
                    print(f"  ❌ {C_PINK}{link_name:<25}{C_RESET} {C_RED}(Missing link - run 'omnidrive link' to fix){C_RESET}")
    else:
        print(f"  Mount Point: {C_RED}[OFFLINE]{C_RESET} {DEFAULT_MOUNT_POINT} is not mounted.")
        print(f"  Image File:  {DEFAULT_IMAGE_PATH} " + (f"{C_GREEN}(Exists){C_RESET}" if DEFAULT_IMAGE_PATH.exists() else f"{C_RED}(Not found){C_RESET}"))
        print(f"  Tip: Run {C_GOLD}omnidrive mount{C_RESET} to mount the virtual disk.")

def mount_disk():
    header()
    if is_mounted():
        print(f"ℹ️  OmniDrive is already mounted at {DEFAULT_MOUNT_POINT}")
        return
    
    if not DEFAULT_IMAGE_PATH.exists():
        print(f"{C_RED}❌ Error:{C_RESET} Sparse image file not found at {DEFAULT_IMAGE_PATH}")
        print(f"   Please run {C_GOLD}omnidrive create{C_RESET} first to generate a new virtual disk.")
        sys.exit(1)
        
    print(f"📡 Attaching virtual disk image: {DEFAULT_IMAGE_PATH}...")
    run_cmd(f"hdiutil attach {DEFAULT_IMAGE_PATH}")
    
    if is_mounted():
        print(f"🚀 {C_GREEN}OmniDrive mounted successfully at {DEFAULT_MOUNT_POINT}{C_RESET}")
        # Repair links automatically on mount
        repair_links(silent=True)
    else:
        print(f"{C_RED}❌ Mount failed. Please check hdiutil manually.{C_RESET}")
        sys.exit(1)

def unmount_disk():
    header()
    if not is_mounted():
        print(f"ℹ️  OmniDrive is not currently mounted.")
        return
        
    print(f"🔌 Detaching virtual disk from {DEFAULT_MOUNT_POINT}...")
    run_cmd(f"hdiutil detach {DEFAULT_MOUNT_POINT}")
    
    if not is_mounted():
        print(f"✨ {C_GREEN}OmniDrive detached successfully.{C_RESET}")
    else:
        print(f"{C_RED}❌ Detaching failed. Disk might be in use by another process.{C_RESET}")
        sys.exit(1)

def repair_links(silent=False):
    if not is_mounted():
        if not silent:
            header()
            print(f"{C_RED}❌ Error: OmniDrive must be mounted before linking.{C_RESET}")
            print(f"   Run {C_GOLD}omnidrive mount{C_RESET} first.")
        return
        
    if not silent:
        header()
        print(f"🛠️  {C_BOLD}REPAIRING OMNIDRIVE SYMLINKS{C_RESET}")
        
    for link_name, target in DEFAULT_LINKS.items():
        link_path = DEFAULT_MOUNT_POINT / link_name
        
        # Clean up existing invalid symlink/file
        if link_path.is_symlink() or link_path.exists():
            try:
                if link_path.is_dir() and not link_path.is_symlink():
                    shutil.rmtree(link_path)
                else:
                    link_path.unlink()
            except Exception as e:
                if not silent:
                    print(f"  ⚠️  Failed to remove old path {link_path}: {e}")
                continue
                
        # Create new symlink
        try:
            os.symlink(target, link_path)
            if not silent:
                print(f"  ✅ Created link: {C_PINK}{link_name:<25}{C_RESET} -> {target}")
        except Exception as e:
            if not silent:
                print(f"  ❌ Failed to create link {link_name}: {e}")
                
    if not silent:
        print(f"\n✨ Symlink updates complete.")

def create_disk(size):
    header()
    image_dir = DEFAULT_IMAGE_PATH.parent
    image_dir.mkdir(parents=True, exist_ok=True)
    
    if DEFAULT_IMAGE_PATH.exists():
        print(f"⚠️  {C_RED}Warning:{C_RESET} An OmniDrive image already exists at {DEFAULT_IMAGE_PATH}")
        confirm = input("Are you sure you want to overwrite it? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Operation aborted.")
            return
            
        # Unmount if mounted
        if is_mounted():
            print("Unmounting active disk first...")
            run_cmd(f"hdiutil detach {DEFAULT_MOUNT_POINT}", check=False)
            
        DEFAULT_IMAGE_PATH.unlink()
        
    print(f"💿 Creating a new virtual disk ({size}) at {DEFAULT_IMAGE_PATH}...")
    
    # We create a sparsebundle or a sparseimage. Since it ends with .sparseimage we use SPARSE type
    run_cmd(f"hdiutil create -size {size} -type SPARSE -fs APFS -volname OmniDrive {DEFAULT_IMAGE_PATH.with_suffix('')}")
    
    # hdiutil create auto adds .sparseimage or .sparsebundle, so we make sure it's at the target path
    created_path = DEFAULT_IMAGE_PATH.with_suffix(".sparseimage")
    if created_path.exists() and created_path != DEFAULT_IMAGE_PATH:
        shutil.move(created_path, DEFAULT_IMAGE_PATH)
        
    print(f"🚀 {C_GREEN}New virtual disk created successfully!{C_RESET}")
    print(f"   Run {C_GOLD}omnidrive mount{C_RESET} to mount and build link structures.")

def show_share_info():
    header()
    print(f"🌐 {C_BOLD}CROSS-DEVICE SHARING (SMB over Tailscale / LAN){C_RESET}")
    print("OmniDrive can be easily accessed from other Macs or devices in your private network.")
    print("\n1. Mount SMB share from another client (e.g. MacBook Pro):")
    print(f"   {C_GOLD}mount_smbfs //jaegwan.kim:1324@<MacMini-IP>/OmniDrive ~/Desktop/MacMini_OmniDrive{C_RESET}")
    print("\n2. Connect via SSH interactive command-center:")
    print(f"   {C_GOLD}ssh -t jaegwan.kim@<MacMini-IP> \"tmux attach -t omnidrive || tmux new -s omnidrive\"{C_RESET}")
    print("\n3. Status on Local Machine:")
    print("   Ensure Tailscale is active and the host is reachable.")

def main():
    parser = argparse.ArgumentParser(
        description="OmniDrive - Unified Virtual Disk Storage & Symlink Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")
    
    subparsers.add_parser("status", aliases=["info"], help="Show mounting and symlink status")
    subparsers.add_parser("mount", aliases=["attach"], help="Mount the virtual disk image")
    subparsers.add_parser("unmount", aliases=["detach", "umount"], help="Unmount the virtual disk image")
    subparsers.add_parser("link", help="Repair/rebuild standard symlink paths")
    subparsers.add_parser("share", help="Display sharing commands and remote access options")
    
    create_parser = subparsers.add_parser("create", help="Create a new virtual disk image")
    create_parser.add_argument("-s", "--size", default="10g", help="Virtual disk size (e.g., 10g, 50g, 100g)")
    
    args = parser.parse_args()
    
    # Default to status if no command given
    if not args.command:
        check_status()
        return

    if args.command in ["status", "info"]:
        check_status()
    elif args.command in ["mount", "attach"]:
        mount_disk()
    elif args.command in ["unmount", "detach", "umount"]:
        unmount_disk()
    elif args.command == "link":
        repair_links()
    elif args.command == "create":
        create_disk(args.size)
    elif args.command == "share":
        show_share_info()

if __name__ == "__main__":
    main()
