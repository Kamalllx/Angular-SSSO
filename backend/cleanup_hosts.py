#!/usr/bin/env python3
"""
Emergency cleanup script to unblock websites
Run this if the main program crashes and leaves websites blocked
"""

import os
import platform
import sys

def get_hosts_file_path():
    """Get the hosts file path for the current OS"""
    if platform.system() == "Windows":
        return r"C:\Windows\System32\drivers\etc\hosts"
    else:  # Linux/macOS
        return "/etc/hosts"

def unblock_all_websites():
    """Emergency unblock all websites"""
    hosts_file = get_hosts_file_path()
    block_marker = "# Smart Study Orchestrator - START"
    block_end_marker = "# Smart Study Orchestrator - END"
    
    try:
        # Read hosts file
        with open(hosts_file, 'r') as f:
            lines = f.readlines()
        
        # Remove blocked entries
        new_lines = []
        skip_lines = False
        removed_count = 0
        
        for line in lines:
            if block_marker in line:
                skip_lines = True
                continue
            elif block_end_marker in line:
                skip_lines = False
                continue
            
            if skip_lines:
                removed_count += 1
            else:
                new_lines.append(line)
        
        # Write back to hosts file
        with open(hosts_file, 'w') as f:
            f.writelines(new_lines)
        
        print(f"✅ Successfully removed {removed_count} blocked website entries")
        print("🌐 All websites should now be accessible")
        
        # Flush DNS cache
        if platform.system() == "Windows":
            os.system("ipconfig /flushdns")
        elif platform.system() == "Darwin":  # macOS
            os.system("sudo dscacheutil -flushcache")
        elif platform.system() == "Linux":
            os.system("sudo systemctl restart systemd-resolved")
        
        print("✅ DNS cache flushed")
        
    except PermissionError:
        print("❌ Permission denied!")
        if platform.system() == "Windows":
            print("Run this script as Administrator")
        else:
            print("Run this script with sudo: sudo python cleanup_hosts.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔓 Emergency Website Unblock Tool")
    print("=" * 40)
    unblock_all_websites()
    input("\nPress Enter to exit...")
