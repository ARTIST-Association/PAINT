import os
import subprocess
import sys

import requests

# Configuration
MOUNT_POINT = "/mnt/lsdf"
WEBSITE_URL = "https://paint-database.org"
VM_HOST = "141.52.215.85"
LOCK_FILE = "/tmp/monitor.lock"

# Initialize email content
email_subject = "PAINT has an issue - ATTENTION REQUIRED"
email_body = []


# Functions for each test
def is_mount_available(mount_point: str):
    """Check if the mount point is available."""
    return os.path.ismount(mount_point)


def is_website_reachable(url: str):
    """Check if the website is reachable by sending a request."""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def is_vm_reachable(host):
    """Check if the VM is reachable using the 'ping' command."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


def add_error(message):
    """Add an error message to the email body."""
    email_body.append(message)


# Main function
if __name__ == "__main__":
    # Check if the lock file exists
    if os.path.exists(LOCK_FILE):
        sys.exit(0)

    # Check each service and record errors
    if not is_mount_available(MOUNT_POINT):
        add_error(
            f"❌ Mount Check Failed: The SSHFS mount at {MOUNT_POINT} is not working."
        )

    if not is_website_reachable(WEBSITE_URL):
        add_error(f"❌ Website Check Failed: {WEBSITE_URL} is not reachable.")

    if not is_vm_reachable(VM_HOST):
        add_error(f"❌ VM Check Failed: Unable to ping the VM at {VM_HOST}.")

    # If there are any errors, send an email and create a lock file
    if email_body:
        # Add header to email body
        email_body.insert(0, "🚨 System Monitoring Alert 🚨\n")
        email_body.insert(1, "The following issues have been detected:\n")
        email_body.append("\nPlease address these issues immediately.")

        # Print email content for cron to send as an email
        print(f"Subject: {email_subject}\n")
        print("\n".join(email_body))

        # Create a lock file to prevent repeated alerts
        with open(LOCK_FILE, "w") as f:
            f.write("\n".join(email_body))

        sys.exit(1)  # Exit with an error status to indicate a problem

    # Silent exit if no errors
    add_error(
        f"❌ Mount Check Failed: The SSHFS mount at {MOUNT_POINT} is not working."
    )
    email_body.insert(0, "EVERYTHING IS ACTUALLY OK")
    email_body.insert(1, "🚨 System Monitoring Alert 🚨\n")
    email_body.insert(2, "The following issues have been detected:\n")
    # Print email content for cron to send as an email
    print(f"Subject: {email_subject}\n")
    print("\n".join(email_body))
    sys.exit(0)
