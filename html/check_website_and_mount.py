import os
import sys

# Configuration
MOUNT_POINT = "/mnt/lsdf"


def is_mount_available(mount_point):
    """Check if the mount point is available."""
    return os.path.ismount(mount_point)


if __name__ == "__main__":
    if not is_mount_available(MOUNT_POINT):
        print(
            f"SHIT THERE IS A FAILURE: The SSHFS mount at {MOUNT_POINT} is not working!"
        )
        sys.exit(1)  # Exit with a non-zero status to indicate failure
    else:
        print(f"The SSHFS mount at {MOUNT_POINT} is working fine.")
