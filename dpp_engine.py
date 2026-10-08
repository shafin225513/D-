# Save this file exactly as: dpp_engine.py
import re
import time
import sys
import os
import subprocess

class DPlusPlusDevOpsEngine:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.registry = {}
        self.settings = {}
        self.rule = {}
        self.last_mod_time = 0.0
        self.modification_count = 0

    def compile(self):
        try:
            with open(self.filepath, "r") as f:
                dpp_code = f.read()
        except FileNotFoundError:
            print(f" Error: Could not find D++ file '{self.filepath}'")
            sys.exit(1)

        print(f" [D++ ENGINE] Compiling system parameters from: '{self.filepath}'...")

        # Parse RESOURCES & CONFIGURATIONS
        for line in dpp_code.splitlines():
            line = line.strip()
            if line.startswith("RESOURCE"):
                res_match = re.match(r"RESOURCE\s+(\w+)\s+(\w+)\s+(IDENTIFIED\s+BY|LOCATED\s+AT)\s+\"(.+)\"", line)
                if res_match:
                    res_type, res_name, _, res_addr = res_match.groups()
                    self.registry[res_name] = {"type": res_type, "address": res_addr}
                    print(f"    Linked RESOURCE [{res_type.upper()}]: '{res_name}' -> {res_addr}")
            elif line.startswith("SET"):
                set_match = re.match(r"SET\s+(\w+)\s+=\s+(.+)", line)
                if set_match:
                    param, val = set_match.groups()
                    self.settings[param] = val.strip()
                    print(f"    Mapped SYSTEM CONFIG: {param} = {val}")

        # Parse DevOps Behavioral Rules
        rule_pattern = (
            r"WHEN\s+([a-zA-Z0-9_\.]+)\s+(IS GREATER THAN)\s+(\d+)\s+FOR\s+(\d+)\s+seconds\s+"
            r"TRIGGER\s+([a-zA-Z0-9_]+)\s+(ON)\s+"
            r"UNTIL\s+([a-zA-Z0-9_\.]+)\s+(IS EQUAL TO)\s+\"(.+)\""
        )
        match = re.search(rule_pattern, dpp_code)
        if match:
            self.rule = {
                "target_metric": match.group(1), # test_folder.modified_count
                "threshold": int(match.group(3)),
                "duration": int(match.group(4)),
                "action_resource": match.group(5), # test_runner
                "target_state": match.group(6),
            }
            print("    Behavioral Pipeline built successfully!\n")
        else:
            print(" Compilation Error: Invalid plain-English grammar mapping.")
            sys.exit(1)

    def scan_target_directory(self, folder_path: str) -> bool:
        """Checks if files inside the directory have been saved/modified."""
        if not os.path.exists(folder_path):
            return False
            
        current_max_mod = 0.0
        # Loop through files to find latest modification timestamp
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    mod_time = os.path.getmtime(file_path)
                    if mod_time > current_max_mod:
                        current_max_mod = mod_time
                except OSError:
                    pass

        # If a file was saved, tick our modification tracker count upward
        if self.last_mod_time == 0.0:
            self.last_mod_time = current_max_mod
            return False

        if current_max_mod > self.last_mod_time:
            self.last_mod_time = current_max_mod
            return True
        return False

    def run(self):
        folder_alias = self.rule["target_metric"].split(".")[0]
        actual_folder = self.registry[folder_alias]["address"]
        command_to_run = self.registry[self.rule["action_resource"]]["address"]
        
        seconds_sustained = 0
        sentinel_active = False

        print(f"--- LIVE DEVOPS SENTINEL STARTING ---")
        print(f"Monitoring folder changes at: '{actual_folder}'\n")

        clock = 0
        while True:
            clock += 1
            # 1. Gather real environmental metrics from your OS
            was_modified = self.scan_target_directory(actual_folder)
            if was_modified:
                self.modification_count += 1
                print(f"    [FILE SYSTEM EVENT] Change detected inside '{actual_folder}'! Total edits = {self.modification_count}")

            print(f"[Clock: {clock}s] Current Edits Count = {self.modification_count} (Sustained active window: {seconds_sustained}s)")

            # 2. Check logic conditions against text rules
            if self.modification_count > self.rule["threshold"]:
                seconds_sustained += 1
            else:
                seconds_sustained = 0

            # 3. Trigger target automated system processes
            if seconds_sustained >= self.rule["duration"] and not sentinel_active:
                print(f"\n    [D++ RULE ENGAGED] Developer sprint pattern matched ({self.rule['duration']}s continuous editing)!")
                print(f"   Executing automation script: '{command_to_run}'")
                
                # Execute the real terminal command mapped in the resource block
                subprocess.run(command_to_run, shell=True)
                
                # Reset counts post-execution loop
                self.modification_count = 0
                seconds_sustained = 0
                print("    [D++ RECOVERY] Automation suite complete. Returning to watch state.\n")

            time.sleep(1)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "sentinel.dpp"
    engine = DPlusPlusDevOpsEngine(target)
    engine.compile()
    engine.run()
