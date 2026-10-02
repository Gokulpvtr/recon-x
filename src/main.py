#!/usr/bin/env python3
import sys
import argparse
import os
import warnings
from datetime import datetime

# Suppress SSL warnings
warnings.filterwarnings('ignore')

try:
    from src.enumerator import run_enumeration
    from src.prober import run_probing
    from src.detector import run_detection
    from src.reporter import generate_report
except ImportError as e:
    print(f"Error: Failed to import modules. Make sure you're in the correct directory.")
    print(f"Run: python -m src.main -d example.com")
    sys.exit(1)

# Hacker theme colors
BRIGHT_GREEN = '\033[1;92m'
CYAN = '\033[1;96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def print_banner():
    banner = f"""{BRIGHT_GREEN}
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║       ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗     ██╗  ██╗           ║
║       ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║     ╚██╗██╔╝           ║
║       ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║█████╗╚███╔╝            ║
║       ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║╚════╝██╔██╗            ║
║       ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║     ██╔╝ ██╗           ║
║       ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝     ╚═╝  ╚═╝           ║
║                                                                          ║                                                                
║                           v1.0                                           ║
║                                                                          ║
║         Automated Reconnaissance & Enumeration                           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
{RESET}

{BRIGHT_GREEN}══════════════════════════════════════════════════════════════════{RESET}
{CYAN}         🎯 Offensive Security Reconnaissance Suite{RESET}
{BRIGHT_GREEN}══════════════════════════════════════════════════════════════════{RESET}

{GREEN}  ┌─────────────────────────────────────────────────────┐{RESET}
{GREEN}  │ 📌 Version:  1.0                                    │{RESET}
{GREEN}  │ 👤 Owner:    GOKULKRISHNAN S                        │{RESET}
{GREEN}  │ 🔗 GitHub:   @Gokulpvtr                             │{RESET}
{GREEN}  │ 🛡️  Type:     Bug Bounty & Offensive Security       │{RESET}
{GREEN}  └─────────────────────────────────────────────────────┘{RESET}

{BRIGHT_GREEN}══════════════════════════════════════════════════════════════════{RESET}

{YELLOW}
        ╔══════════════════════════════════════════╗
        ║  🔍 SUBDOMAIN SCAN    ✓ LIVE DETECTION  ║
        ║  🛠️  TECH FINGERPRINT ✓ SCREENSHOTS     ║
        ║  📊 REPORTING         ✓ JSON + HTML     ║
        ╚══════════════════════════════════════════╝
{RESET}
"""
    
    print(banner)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="🎯 RECON-X: Automated reconnaissance for offensive security",
        epilog="Example: python -m src.main -d example.com -t 15"
    )
    parser.add_argument('-d', '--domain', required=True, help='🎯 Target domain')
    parser.add_argument('-t', '--threads', type=int, default=10, help='⚡ Thread count (default: 10)')
    parser.add_argument('--no-probe', action='store_true', help='🚫 Skip live host probing')
    parser.add_argument('--no-detect', action='store_true', help='🚫 Skip tech detection')
    parser.add_argument('--no-report', action='store_true', help='🚫 Skip HTML report')
    parser.add_argument('--screenshot', action='store_true', help='📸 Enable screenshots')
    parser.add_argument('--full', action='store_true', help='🔍 Full enumeration')
    
    args = parser.parse_args()
    
    print(f"{CYAN}\n🔄 STARTING RECONNAISSANCE...{RESET}\n")
    print(f"{GREEN}  [✓]{RESET} 🎯 Target: {BRIGHT_GREEN}{args.domain}{RESET}")
    print(f"{GREEN}  [✓]{RESET} ⚡ Threads: {BRIGHT_GREEN}{args.threads}{RESET}")
    print(f"{GREEN}  [✓]{RESET} 🔍 Probe Hosts: {BRIGHT_GREEN}{'No' if args.no_probe else 'Yes'}{RESET}")
    print(f"{GREEN}  [✓]{RESET} 🛠️  Tech Detection: {BRIGHT_GREEN}{'No' if args.no_detect else 'Yes'}{RESET}")
    print(f"{GREEN}  [✓]{RESET} 📊 Generate Report: {BRIGHT_GREEN}{'No' if args.no_report else 'Yes'}{RESET}")
    
    print(f"\n{YELLOW}⚠️  AUTHORIZATION CHECK{RESET}")
    print(f"{YELLOW}  [!]{RESET} Ensure you have written permission to scan: {BRIGHT_GREEN}{args.domain}{RESET}\n")
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Phase 1: Subdomain Enumeration
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{BRIGHT_GREEN}PHASE 1: SUBDOMAIN ENUMERATION{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    
    enum_output_file = f"output/{args.domain}_subdomains.json"
    subdomains = run_enumeration(args.domain, enum_output_file, threads=args.threads)
    
    # Phase 2: Live Host Probing
    live_hosts = {}
    if not args.no_probe and len(subdomains) > 0:
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{BRIGHT_GREEN}PHASE 2: LIVE HOST PROBING{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        probe_output_file = f"output/{args.domain}_live_hosts.json"
        live_hosts = run_probing(subdomains, probe_output_file, threads=args.threads)
    
    # Phase 3: Tech Detection
    tech_data = {}
    if not args.no_detect and len(live_hosts) > 0:
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{BRIGHT_GREEN}PHASE 3: TECHNOLOGY FINGERPRINTING{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        detect_output_file = f"output/{args.domain}_tech_detection.json"
        tech_data, tech_summary = run_detection(live_hosts, detect_output_file, threads=args.threads)
    
    # Phase 4: Report Generation
    if not args.no_report:
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{BRIGHT_GREEN}PHASE 4: REPORT GENERATION{RESET}")
        print(f"{CYAN}{'='*60}{RESET}\n")
        
        report_output_file = f"output/{args.domain}_report.html"
        generate_report(args.domain, subdomains, live_hosts, tech_data, report_output_file)
    
    # Summary
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{GREEN}[✓] RECONNAISSANCE COMPLETE!{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    print(f"{GREEN}📊 OUTPUT FILES:{RESET}")
    print(f"{CYAN}  [1]{RESET} Subdomains: {BRIGHT_GREEN}output/{args.domain}_subdomains.json{RESET}")
    if live_hosts:
        print(f"{CYAN}  [2]{RESET} Live hosts: {BRIGHT_GREEN}output/{args.domain}_live_hosts.json{RESET}")
    if tech_data:
        print(f"{CYAN}  [3]{RESET} Tech detection: {BRIGHT_GREEN}output/{args.domain}_tech_detection.json{RESET}")
    if not args.no_report:
        print(f"{CYAN}  [4]{RESET} 📄 HTML Report: {BRIGHT_GREEN}output/{args.domain}_report.html{RESET}")
    
    print(f"\n{YELLOW}💡 TIP:{RESET} Open the HTML report in your browser to view results!\n")

if __name__ == "__main__":
    main()
