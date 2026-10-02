#!/usr/bin/env python3
import sys
import argparse
import os
from datetime import datetime
from src.enumerator import run_enumeration
from src.prober import run_probing
from src.detector import run_detection

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
║   ██████╗ ███████╗ ██████╗ ██████╗ ██╗ ██╗    ██╗  ██╗                 ║
║   ██╔══██╗██╔════╝██╔════╝██╔═══██╗██║ ██║    ╚██╗██╔╝                 ║
║   ██████╔╝█████╗  ██║     ██║   ██║██║ ██║     ╚███╔╝                  ║
║   ██╔══██╗██╔══╝  ██║     ██║   ██║╚██╗██╔╝     ██╔██╗                 ║
║   ██║  ██║███████╗╚██████╗╚██████╔╝ ╚███╔╝    ██╔╝ ██╗                ║
║   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝  ╚══╝     ╚═╝  ╚═╝                ║
║                                                                          ║
║                           v1.0                                           ║
║                                                                          ║
║         Automated Reconnaissance & Enumeration                          ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
{RESET}

{BRIGHT_GREEN}══════════════════════════════════════════════════════════════════{RESET}
{CYAN}         🎯 Offensive Security Reconnaissance Suite{RESET}
{BRIGHT_GREEN}══════════════════════════════════════════════════════════════════{RESET}

{GREEN}  ┌─────────────────────────────────────────────────────┐{RESET}
{GREEN}  │ 📌 Version:  1.0                                    │{RESET}
{GREEN}  │ 👤 Owner:    Gokulkrishnan S                        │{RESET}
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

def print_network_diagram():
    """Show a cool network diagram"""
    diagram = f"""{CYAN}
    ┏━━━━━━━━━━━━━━┓
    ┃  TARGET.COM  ┃
    ┗━━━┳━━━━━━━━━━┛
        ┃
    ┌───┼───────────────────────┐
    │   │                       │
    ▼   ▼                       ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ sub1.com │  │ sub2.com │  │ sub3.com │
└──────────┘  └──────────┘  └──────────┘
    │ nginx     │ Apache    │ IIS
    │ Django    │ React     │ WordPress
    │           │           │
    ✓ LIVE      ✓ LIVE      ✓ LIVE
{RESET}"""
    return diagram

def print_summary(subdomains, live_hosts, tech_summary):
    """Print summary statistics"""
    summary = f"""{BRIGHT_GREEN}
╔════════════════════════════════════════════╗
║           RECONNAISSANCE SUMMARY           ║
╠════════════════════════════════════════════╣
║ Total Subdomains Found:  {len(subdomains):>20} ║
║ Live Hosts Detected:     {len(live_hosts):>20} ║
║ Responsiveness Rate:     {(len(live_hosts)/max(len(subdomains),1)*100):>18.1f}% ║
╠════════════════════════════════════════════╣
║               TECHNOLOGIES                 ║
╠════════════════════════════════════════════╣
"""
    
    # Add servers
    if tech_summary.get("servers"):
        summary += f"║ Web Servers:                               ║\n"
        for server, count in list(tech_summary["servers"].items())[:3]:
            summary += f"║   • {server}: {count}                            ║\n"
    
    # Add CMS
    if tech_summary.get("cms_found"):
        summary += f"║ CMS Platforms:                             ║\n"
        for cms in tech_summary["cms_found"][:3]:
            summary += f"║   • {cms}                              ║\n"
    
    # Add languages
    if tech_summary.get("languages"):
        summary += f"║ Languages:                                 ║\n"
        for lang in tech_summary["languages"][:3]:
            summary += f"║   • {lang}                              ║\n"
    
    summary += f"╚════════════════════════════════════════════╝{RESET}"
    
    return summary

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
    parser.add_argument('--screenshot', action='store_true', help='📸 Enable screenshots')
    parser.add_argument('--full', action='store_true', help='🔍 Full enumeration')
    
    args = parser.parse_args()
    
    print(f"{CYAN}\n🔄 STARTING RECONNAISSANCE...{RESET}\n")
    print(f"{GREEN}  [✓]{RESET} 🎯 Target: {BRIGHT_GREEN}{args.domain}{RESET}")
    print(f"{GREEN}  [✓]{RESET} ⚡ Threads: {BRIGHT_GREEN}{args.threads}{RESET}")
    print(f"{GREEN}  [✓]{RESET} 🔍 Probe Hosts: {BRIGHT_GREEN}{'No' if args.no_probe else 'Yes'}{RESET}")
    print(f"{GREEN}  [✓]{RESET} 🛠️  Tech Detection: {BRIGHT_GREEN}{'No' if args.no_detect else 'Yes'}{RESET}")
    print(f"{GREEN}  [✓]{RESET} 📸 Screenshots: {BRIGHT_GREEN}{'Yes' if args.screenshot else 'No'}{RESET}")
    print(f"{GREEN}  [✓]{RESET} 🔍 Full Enum: {BRIGHT_GREEN}{'Yes' if args.full else 'No'}{RESET}")
    
    print(f"\n{YELLOW}⚠️  AUTHORIZATION CHECK{RESET}")
    print(f"{YELLOW}  [!]{RESET} Ensure you have written permission to scan: {BRIGHT_GREEN}{args.domain}{RESET}\n")
    
    # Create output directory if it doesn't exist
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
    tech_summary = {}
    if not args.no_detect and len(live_hosts) > 0:
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{BRIGHT_GREEN}PHASE 3: TECHNOLOGY FINGERPRINTING{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        
        detect_output_file = f"output/{args.domain}_tech_detection.json"
        tech_data, tech_summary = run_detection(live_hosts, detect_output_file, threads=args.threads)
    
    # Show network diagram
    print(print_network_diagram())
    
    # Show summary
    print(print_summary(subdomains, live_hosts, tech_summary))
    
    # Final results
    print(f"\n{GREEN}[✓] Reconnaissance Complete!{RESET}")
    print(f"{CYAN}[*] Enumeration: {BRIGHT_GREEN}output/{args.domain}_subdomains.json{RESET}")
    if live_hosts:
        print(f"{CYAN}[*] Live hosts: {BRIGHT_GREEN}output/{args.domain}_live_hosts.json{RESET}")
    if tech_summary:
        print(f"{CYAN}[*] Tech detection: {BRIGHT_GREEN}output/{args.domain}_tech_detection.json{RESET}")
    print()

if __name__ == "__main__":
    main()