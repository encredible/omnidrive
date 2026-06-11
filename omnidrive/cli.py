#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 OMNIDRIVE CLI v1.1 [CROSS-PLATFORM RELEASE]
Unified Virtual Disk Storage & Symlink Manager for macOS, Windows, and Linux
"""

import os
import sys
import argparse
import subprocess
import shutil
import platform
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

# Cross-Platform Configuration
SYSTEM_OS = platform.system()  # 'Darwin' (macOS), 'Windows', 'Linux'

if SYSTEM_OS == 'Darwin':
    DEFAULT_MOUNT_POINT = Path("/Volumes/OmniDrive")
    DEFAULT_IMAGE_PATH = Path.home() / "OmniDrive_System" / "OmniDrive_Jack.sparsebundle.sparseimage"
    DEFAULT_LINKS = {
        "Google Drive": Path.home() / "Library/CloudStorage/GoogleDrive-descartes131@gmail.com",
        "Macintosh HD (Local Mac)": Path("/"),
        "The Ark App": Path.home() / "RewardAggregatorApp",
        "The Ark Repo": Path.home() / "RewardAggregator",
        "iCloud Drive": Path.home() / "Library/Mobile Documents/com~apple~CloudDocs",
    }
elif SYSTEM_OS == 'Windows':
    DEFAULT_MOUNT_POINT = Path.home() / "OmniDrive"
    DEFAULT_IMAGE_PATH = Path.home() / "OmniDrive_System" / "OmniDrive_Jack.vhdx"
    # Windows fallback cloud storage paths
    DEFAULT_LINKS = {
        "Google Drive": Path("G:/My Drive") if Path("G:/My Drive").exists() else Path.home() / "Google Drive",
        "System Drive (C)": Path("C:/"),
        "The Ark App": Path.home() / "RewardAggregatorApp",
        "The Ark Repo": Path.home() / "RewardAggregator",
        "iCloud Drive": Path.home() / "iCloudDrive",
    }
else:  # Linux / fallback
    DEFAULT_MOUNT_POINT = Path.home() / "OmniDrive"
    DEFAULT_IMAGE_PATH = Path.home() / "OmniDrive_System" / "OmniDrive_Jack.img"
    DEFAULT_LINKS = {
        "Google Drive": Path.home() / "GoogleDrive",
        "Root Directory (/)": Path("/"),
        "The Ark App": Path.home() / "RewardAggregatorApp",
        "The Ark Repo": Path.home() / "RewardAggregator",
        "iCloud Drive": Path.home() / "iCloudDrive",
    }

def header():
    print(f"{C_MAGENTA}{C_BOLD}✨ OMNIDRIVE CONTROL CENTER v1.1 [{SYSTEM_OS.upper()} MODE] ✨{C_RESET}")
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
    if SYSTEM_OS == 'Darwin':
        out = run_cmd("mount", check=False)
        return str(mount_point) in out
    else:
        # On Windows/Linux emulated mode, we treat it as mounted if the mount point directory exists
        # and has our symlinks in it.
        return mount_point.exists() and any((mount_point / name).exists() or (mount_point / name).is_symlink() for name in DEFAULT_LINKS)

def check_status():
    header()
    print(f"💾 {C_BOLD}MOUNT STATUS{C_RESET}")
    mounted = is_mounted()
    
    if mounted:
        print(f"  Mount Point: {C_GREEN}[ONLINE]{C_RESET} {DEFAULT_MOUNT_POINT}")
        
        # Get storage stats
        try:
            total, used, free = shutil.disk_usage(DEFAULT_MOUNT_POINT)
            total_gb = total / (1024**3)
            used_gb = used / (1024**3)
            free_gb = free / (1024**3)
            used_percent = (used / total) * 100 if total > 0 else 0
            
            print(f"  Capacity:    {C_GOLD}{total_gb:.2f} GB{C_RESET} total | {C_GOLD}{used_gb:.2f} GB{C_RESET} used | {C_GOLD}{free_gb:.2f} GB{C_RESET} free")
            print(f"  Usage:       {C_PINK}[{'#' * int(used_percent/5)}{'-' * (20 - int(used_percent/5))}] {used_percent:.1f}%{C_RESET}")
        except Exception as e:
            print(f"  Capacity:    {C_RED}Unable to read storage capacity ({e}){C_RESET}")
        
        # Verify symlinks
        print(f"\n🔗 {C_BOLD}UNIFIED SYMLINKS STATUS{C_RESET}")
        for link_name, target in DEFAULT_LINKS.items():
            link_path = DEFAULT_MOUNT_POINT / link_name
            if link_path.is_symlink():
                try:
                    resolved = link_path.resolve()
                    if resolved.exists():
                        print(f"  🟢 {C_PINK}{link_name:<25}{C_RESET} -> {resolved} {C_GREEN}(Valid){C_RESET}")
                    else:
                        print(f"  🔴 {C_PINK}{link_name:<25}{C_RESET} -> {resolved} {C_RED}(Broken target){C_RESET}")
                except Exception:
                    print(f"  🔴 {C_PINK}{link_name:<25}{C_RESET} {C_RED}(Broken link){C_RESET}")
            else:
                if link_path.exists():
                    print(f"  ⚠️  {C_PINK}{link_name:<25}{C_RESET} exists but is not a symlink")
                else:
                    print(f"  ❌ {C_PINK}{link_name:<25}{C_RESET} {C_RED}(Missing link - run 'omnidrive link' to fix){C_RESET}")
    else:
        print(f"  Mount Point: {C_RED}[OFFLINE]{C_RESET} {DEFAULT_MOUNT_POINT} is not mounted.")
        print(f"  Image File:  {DEFAULT_IMAGE_PATH} " + (f"{C_GREEN}(Exists){C_RESET}" if DEFAULT_IMAGE_PATH.exists() else f"{C_RED}(Not found){C_RESET}"))
        print(f"  Tip: Run {C_GOLD}omnidrive mount{C_RESET} to mount the virtual storage.")

def mount_disk():
    header()
    if is_mounted():
        print(f"ℹ️  OmniDrive is already mounted at {DEFAULT_MOUNT_POINT}")
        return
        
    if SYSTEM_OS == 'Darwin':
        if not DEFAULT_IMAGE_PATH.exists():
            print(f"{C_RED}❌ Error:{C_RESET} Sparse image file not found at {DEFAULT_IMAGE_PATH}")
            print(f"   Please run {C_GOLD}omnidrive create{C_RESET} first.")
            sys.exit(1)
        print(f"📡 Attaching virtual disk image on macOS...")
        run_cmd(f"hdiutil attach {DEFAULT_IMAGE_PATH}")
    else:
        # Cross-platform fallback emulated mount: Create directory and links
        print(f"📡 Emulating OmniDrive mount by initializing: {DEFAULT_MOUNT_POINT}...")
        DEFAULT_MOUNT_POINT.mkdir(parents=True, exist_ok=True)
        repair_links(silent=True)
        
    if is_mounted():
        print(f"🚀 {C_GREEN}OmniDrive mounted successfully at {DEFAULT_MOUNT_POINT}{C_RESET}")
        repair_links(silent=True)
    else:
        print(f"{C_RED}❌ Mount failed.{C_RESET}")
        sys.exit(1)

def unmount_disk():
    header()
    if not is_mounted():
        print(f"ℹ️  OmniDrive is not currently mounted.")
        return
        
    print(f"🔌 Detaching virtual storage from {DEFAULT_MOUNT_POINT}...")
    if SYSTEM_OS == 'Darwin':
        run_cmd(f"hdiutil detach {DEFAULT_MOUNT_POINT}")
    else:
        # Cross-platform fallback: Clean up the directory links
        try:
            for link_name in DEFAULT_LINKS:
                link_path = DEFAULT_MOUNT_POINT / link_name
                if link_path.is_symlink() or link_path.exists():
                    if link_path.is_dir() and not link_path.is_symlink():
                        shutil.rmtree(link_path)
                    else:
                        link_path.unlink()
            DEFAULT_MOUNT_POINT.rmdir()
        except Exception as e:
            print(f"{C_RED}❌ Failed to clean up mount directory: {e}{C_RESET}")
            sys.exit(1)
            
    if not is_mounted():
        print(f"✨ {C_GREEN}OmniDrive detached successfully.{C_RESET}")
    else:
        print(f"{C_RED}❌ Detaching failed.{C_RESET}")
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
        print(f"🛠️  {C_BOLD}REPAIRING OMNIDRIVE SYMLINKS ({SYSTEM_OS} Mode){C_RESET}")
        
    for link_name, target in DEFAULT_LINKS.items():
        link_path = DEFAULT_MOUNT_POINT / link_name
        
        # Clean up existing path
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
                
        # Create symlink
        try:
            # target must exist to create link, or we create directories
            if not target.exists():
                # For directories, create placeholder so link works
                if '.' not in target.name:
                    target.mkdir(parents=True, exist_ok=True)
                    
            os.symlink(target, link_path)
            if not silent:
                print(f"  ✅ Created link: {C_PINK}{link_name:<25}{C_RESET} -> {target}")
        except Exception as e:
            # If symlinks fail (e.g. Windows without developer mode), copy/emulate or log warning
            try:
                if SYSTEM_OS == 'Windows':
                    # Fallback to junction point/directory shortcut on Windows if symlink fails
                    subprocess.run(f'mklink /J "{link_path}" "{target}"', shell=True, check=True, capture_output=True)
                    if not silent:
                        print(f"  ✅ Created junction: {C_PINK}{link_name:<25}{C_RESET} -> {target}")
                else:
                    if not silent:
                        print(f"  ❌ Failed to link {link_name} ({e})")
            except Exception as ex:
                if not silent:
                    print(f"  ❌ Failed to link {link_name} ({e} / Fallback: {ex})")
                
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
            
        if is_mounted():
            unmount_disk()
            
        DEFAULT_IMAGE_PATH.unlink()
        
    print(f"💿 Creating a new virtual disk ({size}) at {DEFAULT_IMAGE_PATH}...")
    
    if SYSTEM_OS == 'Darwin':
        run_cmd(f"hdiutil create -size {size} -type SPARSE -fs APFS -volname OmniDrive {DEFAULT_IMAGE_PATH.with_suffix('')}")
        created_path = DEFAULT_IMAGE_PATH.with_suffix(".sparseimage")
        if created_path.exists() and created_path != DEFAULT_IMAGE_PATH:
            shutil.move(created_path, DEFAULT_IMAGE_PATH)
    elif SYSTEM_OS == 'Windows':
        # Create dynamic VHDX file on Windows via PowerShell
        ps_cmd = f"New-VHD -Path '{DEFAULT_IMAGE_PATH}' -SizeBytes {size} -Dynamic"
        run_cmd(f"powershell -Command \"{ps_cmd}\"")
    else:
        # Create standard empty sparse file on Linux
        run_cmd(f"truncate -s {size} {DEFAULT_IMAGE_PATH}")
        
    print(f"🚀 {C_GREEN}New virtual disk created successfully!{C_RESET}")
    print(f"   Run {C_GOLD}omnidrive mount{C_RESET} to mount and build link structures.")

def show_share_info():
    header()
    print(f"🌐 {C_BOLD}CROSS-DEVICE SHARING (WebDAV / SMB){C_RESET}")
    print("OmniDrive can be accessed from ANY operating system (iOS, Android, Windows, macOS, Linux) via network share.")
    print("\n1. WebDAV Endpoint (Accessible on iOS Files / Android Solid Explorer / Browser):")
    print(f"   {C_GOLD}http://<Host-IP>:8000/webdav{C_RESET}")
    print("   Credentials: User: {C_PINK}jack{C_RESET} | Password: {C_PINK}wonyoung{C_RESET}")
    print("\n2. SMB Mount Command for other desktop clients:")
    print(f"   {C_GOLD}mount_smbfs //jaegwan.kim:1324@<Host-IP>/OmniDrive ~/Desktop/MacMini_OmniDrive{C_RESET}")
    print("\n3. SSH tmux workspace:")
    print(f"   {C_GOLD}ssh -t jaegwan.kim@<Host-IP> \"tmux attach -t omnidrive || tmux new -s omnidrive\"{C_RESET}")

def main():
    parser = argparse.ArgumentParser(
        description="OmniDrive - Unified Virtual Disk Storage & Symlink Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")
    
    subparsers.add_parser("status", aliases=["info"], help="Show mounting and symlink status")
    subparsers.add_parser("mount", aliases=["attach"], help="Mount the virtual disk")
    subparsers.add_parser("unmount", aliases=["detach", "umount"], help="Unmount the virtual disk")
    subparsers.add_parser("link", help="Repair/rebuild standard symlink paths")
    subparsers.add_parser("share", help="Display sharing commands and WebDAV access options")
    
    create_parser = subparsers.add_parser("create", help="Create a new virtual disk")
    create_parser.add_argument("-s", "--size", default="10g", help="Virtual disk size (e.g., 10g, 50g, 100g)")
    
    args = parser.parse_args()
    
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
