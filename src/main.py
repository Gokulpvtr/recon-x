#!/usr/bin/env python3
import sys
import argparse
import os
from datetime import datetime
from src.enumerator import run_enumeration

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
    │             │             │
    └─────┬───────┴────┬────────┘
          │            │
       ┌──▼──┐      ┌──▼──┐
       │ 200 │      │ 404 │
       └─────┘      └─────┘
{RESET}"""
    return diagram

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="🎯 RECON-X: Automated reconnaissance for offensive security",
        epilog="Example: python src/main.py -d example.com"
    )
    parser.add_argument('-d', '--domain', required=True, help='🎯 Target domain')
    parser.add_argument('-t', '--threads', type=int, default=10, help='⚡ Thread count')
    parser.add_argument('--screenshot', action='store_true', help='📸 Enable screenshots')
    parser.add_argument('--full', action='store_true', help='🔍 Full enumeration')
    
    args = parser.parse_args()
    
    print(f"{CYAN}\n🔄 STARTING RECONNAISSANCE...{RESET}\n")
    print(f"{GREEN}  [✓]{RESET} 🎯 Target: {BRIGHT_GREEN}{args.domain}{RESET}")
    print(f"{GREEN}  [✓]{RESET} ⚡ Threads: {BRIGHT_GREEN}{args.threads}{RESET}")
    print(f"{GREEN}  [✓]{RESET} 📸 Screenshots: {BRIGHT_GREEN}{'Yes' if args.screenshot else 'No'}{RESET}")
    print(f"{GREEN}  [✓]{RESET} 🔍 Full Enum: {BRIGHT_GREEN}{'Yes' if args.full else 'No'}{RESET}")
    
    print(f"\n{YELLOW}⚠️  AUTHORIZATION CHECK{RESET}")
    print(f"{YELLOW}  [!]{RESET} Ensure you have written permission to scan: {BRIGHT_GREEN}{args.domain}{RESET}\n")
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Run subdomain enumeration
    output_file = f"output/{args.domain}_subdomains.json"
    subdomains = run_enumeration(args.domain, output_file)
    
    # Show network diagram
    print(print_network_diagram())
    
    print(f"\n{GREEN}[✓] Enumeration Complete!{RESET}")
    print(f"{CYAN}[*] Results saved to: {BRIGHT_GREEN}{output_file}{RESET}\n")

if __name__ == "__main__":
    main()