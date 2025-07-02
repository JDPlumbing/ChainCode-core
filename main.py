import argparse
import sys
import subprocess
from pathlib import Path
import os  # ✅ Add this


# Allow absolute-style imports from root folders like `events`, `chaincode`, `tools`
sys.path.append(str(Path(__file__).resolve().parent))


COMMANDS = {
    "generate": "chaincode/generate_chaincode.py",
    "sync": "chaincode/sync_chaincodes.py",
    "decrypt": "tools/decrypt_chaincode.py",
    "sync-links": "tools/sync_links.py",
    "list": "chaincode/chaincode_list.py"
}

def main():
    parser = argparse.ArgumentParser(description="TrustLedger CLI")
    parser.add_argument("command", choices=COMMANDS.keys(), help="Command to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the command")
    args = parser.parse_args()

    cmd = ["python", COMMANDS[args.command]] + args.args
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent)
    subprocess.run(cmd, env=env)


if __name__ == "__main__":
    main()
