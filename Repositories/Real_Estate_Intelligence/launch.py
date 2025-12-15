#!/usr/bin/env python3
"""
Real Estate Intelligence - Autonomous Agent System Launcher
============================================================
This script provides a simple way to launch the autonomous agent system
with different configurations and modes.

Usage:
    python3 launch.py --mode full-cycle
    python3 launch.py --mode monitor
    python3 launch.py --mode diagnose
"""

import sys
import subprocess
import os
import json
from pathlib import Path
from datetime import datetime

# Color codes for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print system header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  🤖 REAL ESTATE INTELLIGENCE - AUTONOMOUS AGENT LAUNCHER       ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")

def print_usage():
    """Print usage information"""
    print(f"{Colors.YELLOW}USAGE:{Colors.RESET}")
    print("  npm run autonomous:full-cycle    # Run once")
    print("  npm run autonomous:monitor       # Run continuously (every 6 hours)")
    print("  npm run autonomous:diagnose      # Diagnose issues")
    print("  npm run autonomous:fix           # Fix problems")
    print("  npm run autonomous:heal          # Recover from errors")
    print("  npm run autonomous:optimize      # Optimize performance")
    print("  npm run autonomous:enhance       # Get recommendations")
    print("")

def check_environment():
    """Check if Node.js and npm are available"""
    print(f"{Colors.YELLOW}Checking environment...{Colors.RESET}")
    
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        node_version = result.stdout.strip()
        print(f"  ✅ Node.js: {node_version}")
    except FileNotFoundError:
        print(f"  ❌ Node.js not found. Please install Node.js from https://nodejs.org")
        return False
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        npm_version = result.stdout.strip()
        print(f"  ✅ npm: {npm_version}")
    except FileNotFoundError:
        print(f"  ❌ npm not found. Please install npm.")
        return False
    
    print()
    return True

def get_autonomous_status():
    """Get status of autonomous system"""
    project_root = Path.cwd()
    
    logs_dir = project_root / "logs" / "autonomous"
    reports_dir = project_root / "reports" / "autonomous"
    
    print(f"{Colors.BLUE}System Status:{Colors.RESET}")
    
    # Check logs
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            print(f"  ✅ Latest Log: {latest_log.name}")
        else:
            print(f"  ⓘ No logs yet (system hasn't run)")
    else:
        print(f"  ⓘ No logs yet (system hasn't run)")
    
    # Check reports
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*.json"))
        if report_files:
            latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
            print(f"  ✅ Latest Report: {latest_report.name}")
            
            # Try to read summary from latest report
            try:
                with open(latest_report, 'r') as f:
                    data = json.load(f)
                    if 'summary' in data:
                        summary = data['summary']
                        print(f"      • Modules: {summary.get('successfulModules', 0)}/{summary.get('totalModules', 0)} successful")
                        print(f"      • Issues: {summary.get('issuesFound', 0)} found")
            except:
                pass
        else:
            print(f"  ⓘ No reports yet (system hasn't run)")
    else:
        print(f"  ⓘ No reports yet (system hasn't run)")
    
    print()

def run_command(mode):
    """Run the autonomous agent in specified mode"""
    print(f"{Colors.GREEN}Starting Autonomous Agent: {mode.upper()}{Colors.RESET}\n")
    
    cmd = f"npm run autonomous:{mode}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Error running command: {e}{Colors.RESET}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        return False
    
    return True

def main():
    """Main entry point"""
    print_header()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Get current status
    get_autonomous_status()
    
    # Show available commands
    print(f"{Colors.GREEN}Available Commands:{Colors.RESET}")
    print()
    print("  1. Full Cycle       npm run autonomous:full-cycle")
    print("  2. Monitor          npm run autonomous:monitor")
    print("  3. Diagnose         npm run autonomous:diagnose")
    print("  4. Fix Issues       npm run autonomous:fix")
    print("  5. Heal             npm run autonomous:heal")
    print("  6. Optimize         npm run autonomous:optimize")
    print("  7. Enhance          npm run autonomous:enhance")
    print()
    
    # Interactive mode
    if len(sys.argv) == 1:
        print(f"{Colors.CYAN}Quick start: npm run autonomous:full-cycle{Colors.RESET}")
        print(f"{Colors.CYAN}Or run:      npm run autonomous:monitor (continuous){Colors.RESET}")
        print()
        print(f"{Colors.YELLOW}For details, see: README_AUTONOMOUS.md{Colors.RESET}\n")
        return 0
    
    # Command line mode
    if len(sys.argv) >= 2:
        mode = sys.argv[1].replace("--mode=", "")
        if mode.startswith("--mode "):
            mode = mode[7:]
        
        valid_modes = ['full-cycle', 'monitor', 'diagnose', 'fix', 'heal', 'optimize', 'enhance', 'agent', 'scheduler']
        
        if mode not in valid_modes:
            print(f"{Colors.RED}Invalid mode: {mode}{Colors.RESET}")
            print(f"Valid modes: {', '.join(valid_modes)}")
            return 1
        
        run_command(mode)
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
