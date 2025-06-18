import os
import subprocess
import sys

import requests

# Configuration
MOUNT_POINT = "/mnt/lsdf"
WEBSITE_URL = "https://paint-database.org"
VM_HOST = "141.52.215.85"
LOCK_FILE = "/tmp/monitor.lock"


def is_mount_available(mount_point: str) -> bool:
    """
    Check if the mount point is available.

    Parameters
    ----------
    mount_point : str
        Mount point being checked.

    Returns
    -------
    bool
        Whether mount point is available.
    """
    return os.path.ismount(mount_point)


def is_website_reachable(url: str) -> bool:
    """
    Check if the website is reachable by sending a request.

    Parameters
    ----------
    url : str
        URL of the website to be checked.

    Returns
    -------
    bool
        Whether the website is reachable by sending a request.
    """
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def is_vm_reachable(host: str) -> bool:
    """
    Check if the VM is reachable using the 'ping' command.

    Parameters
    ----------
    host : str
        The IP address of the VM to be checked.

    Returns
    -------
    bool
        Whether the VM is reachable via ping.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


if __name__ == "__main__":
    # Initialize email body
    email_body = []

    # Check if the mount point is available.
    if not is_mount_available(MOUNT_POINT):
        # If mount is not available, attempt to remount
        cmd = [
            "sudo",
            "sshfs",
            "-o",
            "umask=0,uid=0,gid=0,allow_other,IdentityFile=/home/paint/.ssh/id_rsa",
            "scc-paint-0001@os-login.lsdf.kit.edu:/lsdf/kit/scc/projects/paint",
            MOUNT_POINT,
        ]
        # Suppress printing outputs or errors to avoid extra error emails.
        attempt_remount = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # If remount unsuccessful include error messsage
        if not attempt_remount.returncode == 0:
            email_body.append(
                "❌ The LSDF Mount Check Failed: The SSHFS mount at {MOUNT_POINT} is not working!",
            )
    # Check if the website is reachable.
    if not is_website_reachable(WEBSITE_URL):
        email_body.append("❌ Website Check Failed: {WEBSITE_URL} is not reachable!")
        # Try to restart server.
        try:
            subprocess.run(
                ["/home/paint/run.sh"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            email_body.append("🔁 Attempted to restart PAINT using run.sh.")
        except subprocess.CalledProcessError:
            email_body.append("❌ Failed to execute run.sh to restart PAINT.")

    # Check if the VM is reachable.
    if not is_vm_reachable(VM_HOST):
        email_body.append(f"❌ VM Check Failed: Unable to ping the VM at {VM_HOST}!")

    # First time an error is found, the error should be reported and lock file created
    if email_body and not os.path.exists(LOCK_FILE):
        # Add header to email body.
        email_body.insert(0, "The following issues have been detected with PAINT:\n")
        email_body.append(
            "\nPlease address these issues immediately - until they are addressed, PAINT is down!"
        )

        # Print email content for cron to send as an email.
        print("🚨 PAINT ALERT - There is a Problem with the PAINT Database 🚨\n")
        print("\n".join(email_body))

        # Create a lock file to prevent repeated alerts
        with open(LOCK_FILE, "w") as f:
            f.write("\n".join(email_body))

    # For all future occurrences nothing should be printed, to avoid receiving multiple emails for the same error!
    elif email_body and os.path.exists(LOCK_FILE):
        # Exit without print.
        sys.exit(0)
    elif not email_body and os.path.exists(LOCK_FILE):
        print("🚨 PAINT ALERT - The PAINT Error Detection System is Locked 🚨\n")
        print(
            "It looks like PAINT is running fine, but the lock file has not yet been deleted!\n Please delete the"
            f"lock file located at ``{LOCK_FILE}`` so the error detection system can run as desired!"
        )
