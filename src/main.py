import os
import subprocess
import sys

def run_system():
    print("\nStarting CalTrackAI System...\n")

    compose_path = os.path.join("deployment", "docker-compose.yml")

    if not os.path.exists(compose_path):
        print("ERROR: docker-compose.yml not found in deployment/")
        sys.exit(1)

    try:
        print("Building containers...")
        subprocess.run(["docker-compose", "-f", compose_path, "build"], check=True)

        print("\nLaunching containers...")
        subprocess.run(["docker-compose", "-f", compose_path, "up"], check=True)

    except subprocess.CalledProcessError as e:
        print("\nERROR running docker-compose:", e)
        sys.exit(1)


if __name__ == "__main__":
    print("=======================================")
    print("     CalTrackAI — System Launcher")
    print("=======================================\n")

    run_system()
