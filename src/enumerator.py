#!/usr/bin/env python3
"""
RECON-X Subdomain Enumeration Module
Queries crt.sh API for passive subdomain discovery
"""

import requests
import json
import sys
from datetime import datetime
from typing import Set, List

# Colors
BRIGHT_GREEN = '\033[1;92m'
CYAN = '\033[1;96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

class SubdomainEnumerator:
    def __init__(self, domain: str, timeout: int = 5):
        """Initialize enumerator with target domain"""
        self.domain = domain
        self.timeout = timeout
        self.subdomains = set()
        self.crt_sh_api = "https://crt.sh"
        
    def query_crt_sh(self) -> Set[str]:
        """
        Query crt.sh API for subdomains
        crt.sh is a public CT (Certificate Transparency) log search
        """
        try:
            print(f"{CYAN}  [*]{RESET} Querying {BRIGHT_GREEN}crt.sh{RESET}...")
            
            # API endpoint for JSON response
            url = f"{self.crt_sh_api}/?q=%.{self.domain}&output=json"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Extract unique subdomains
                    for entry in data:
                        # name_value contains comma-separated names
                        names = entry.get('name_value', '').split('\n')
                        for name in names:
                            name = name.strip().lower()
                            if name and self.domain in name:
                                self.subdomains.add(name)
                    
                    print(f"{GREEN}  [+]{RESET} Found {BRIGHT_GREEN}{len(self.subdomains)}{RESET} subdomains from crt.sh")
                    return self.subdomains
                    
                except json.JSONDecodeError:
                    print(f"{RED}  [!]{RESET} Error parsing crt.sh response")
                    return set()
            else:
                print(f"{RED}  [!]{RESET} crt.sh returned status code {response.status_code}")
                return set()
                
        except requests.exceptions.Timeout:
            print(f"{RED}  [!]{RESET} crt.sh request timed out")
            return set()
        except requests.exceptions.RequestException as e:
            print(f"{RED}  [!]{RESET} Error querying crt.sh: {str(e)}")
            return set()
    
    def deduplicate(self) -> Set[str]:
        """Remove duplicate subdomains"""
        print(f"{CYAN}  [*]{RESET} Deduplicating results...")
        unique = set(self.subdomains)
        print(f"{GREEN}  [+]{RESET} After deduplication: {BRIGHT_GREEN}{len(unique)}{RESET} unique subdomains")
        return unique
    
    def save_to_json(self, output_path: str):
        """Save subdomains to JSON file"""
        try:
            # Sort subdomains alphabetically
            sorted_subs = sorted(list(self.subdomains))
            
            output_data = {
                "domain": self.domain,
                "timestamp": datetime.now().isoformat(),
                "total_count": len(sorted_subs),
                "subdomains": sorted_subs
            }
            
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"{GREEN}  [+]{RESET} Results saved to: {BRIGHT_GREEN}{output_path}{RESET}")
            return True
            
        except Exception as e:
            print(f"{RED}  [!]{RESET} Error saving to JSON: {str(e)}")
            return False
    
    def enumerate(self) -> Set[str]:
        """
        Main enumeration method
        Run all enumeration techniques
        """
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{BRIGHT_GREEN}🔍 SUBDOMAIN ENUMERATION STARTED{RESET}")
        print(f"{CYAN}{'='*60}{RESET}\n")
        
        print(f"{GREEN}[*] Target: {BRIGHT_GREEN}{self.domain}{RESET}\n")
        
        # Query crt.sh
        self.query_crt_sh()
        
        # Deduplicate
        self.deduplicate()
        
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{GREEN}[✓] Total Subdomains Found: {BRIGHT_GREEN}{len(self.subdomains)}{RESET}")
        print(f"{CYAN}{'='*60}{RESET}\n")
        
        return self.subdomains


def run_enumeration(domain: str, output_file: str = None) -> Set[str]:
    """
    Convenience function to run enumeration
    """
    enumerator = SubdomainEnumerator(domain)
    subdomains = enumerator.enumerate()
    
    if output_file:
        enumerator.save_to_json(output_file)
    
    return subdomains