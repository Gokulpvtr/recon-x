#!/usr/bin/env python3
"""
RECON-X Subdomain Enumeration Module
Queries crt.sh API + DNS brute-force for subdomain discovery
Uses threading for faster enumeration
"""

import requests
import json
import sys
import dns.resolver
import dns.rdatatype
from datetime import datetime
from typing import Set, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

# Colors
BRIGHT_GREEN = '\033[1;92m'
CYAN = '\033[1;96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

# Thread lock for safe printing
print_lock = threading.Lock()

class SubdomainEnumerator:
    def __init__(self, domain: str, timeout: int = 5, threads: int = 10):
        """Initialize enumerator with target domain"""
        self.domain = domain
        self.timeout = timeout
        self.threads = threads
        self.subdomains = set()
        self.crt_sh_api = "https://crt.sh"
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = timeout
        self.dns_resolver.lifetime = timeout
        self.wordlist = self.load_wordlist()
        
    def load_wordlist(self) -> List[str]:
        """Load subdomains from wordlist"""
        try:
            with open('wordlists/subdomains.txt', 'r') as f:
                return [line.strip().lower() for line in f if line.strip()]
        except FileNotFoundError:
            with print_lock:
                print(f"{YELLOW}  [!]{RESET} Wordlist not found, using basic list")
            return ['www', 'mail', 'ftp', 'smtp', 'api', 'admin', 'test', 'dev', 'staging', 'cdn', 'static']
    
    def query_crt_sh(self) -> Set[str]:
        """
        Query crt.sh API for subdomains
        Includes retry logic for failures
        """
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                with print_lock:
                    print(f"{CYAN}  [*]{RESET} Querying {BRIGHT_GREEN}crt.sh{RESET} (attempt {attempt + 1}/{max_retries})...")
                
                # API endpoint for JSON response
                url = f"{self.crt_sh_api}/?q=%.{self.domain}&output=json"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        with print_lock:
                            print(f"{CYAN}  [*]{RESET} crt.sh returned {BRIGHT_GREEN}{len(data)}{RESET} certificates")
                        
                        # Extract unique subdomains
                        for entry in data:
                            names = entry.get('name_value', '').split('\n')
                            for name in names:
                                name = name.strip().lower()
                                if name and self.domain in name:
                                    self.subdomains.add(name)
                        
                        with print_lock:
                            print(f"{GREEN}  [+]{RESET} Found {BRIGHT_GREEN}{len(self.subdomains)}{RESET} subdomains from crt.sh")
                        return self.subdomains
                        
                    except json.JSONDecodeError:
                        with print_lock:
                            print(f"{RED}  [!]{RESET} Error parsing crt.sh response")
                        
                elif response.status_code == 502:
                    with print_lock:
                        print(f"{YELLOW}  [!]{RESET} crt.sh is temporarily down (502). Retrying in {retry_delay}s...")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    continue
                else:
                    with print_lock:
                        print(f"{RED}  [!]{RESET} crt.sh returned status code {response.status_code}")
                    
            except requests.exceptions.Timeout:
                with print_lock:
                    print(f"{YELLOW}  [!]{RESET} crt.sh request timed out. Trying fallback method...")
                
            except requests.exceptions.RequestException as e:
                with print_lock:
                    print(f"{YELLOW}  [!]{RESET} Error querying crt.sh: {str(e)}")
        
        with print_lock:
            print(f"{YELLOW}  [!]{RESET} crt.sh unavailable, using DNS brute-force method")
        return self.subdomains
    
    def dns_brute_force(self) -> Set[str]:
        """
        DNS brute-force enumeration using wordlist
        Tests common subdomain names
        """
        try:
            with print_lock:
                print(f"\n{CYAN}  [*]{RESET} Starting DNS brute-force with {BRIGHT_GREEN}{self.threads}{RESET} threads...")
                print(f"{CYAN}  [*]{RESET} Testing {BRIGHT_GREEN}{len(self.wordlist)}{RESET} subdomains...\n")
            
            # Use ThreadPoolExecutor for parallel DNS lookups
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {}
                for word in self.wordlist:
                    subdomain = f"{word}.{self.domain}"
                    future = executor.submit(self.dns_lookup, subdomain)
                    futures[future] = subdomain
                
                # Process completed tasks
                completed = 0
                for future in as_completed(futures):
                    subdomain = futures[future]
                    completed += 1
                    
                    try:
                        result = future.result()
                        if result:
                            self.subdomains.add(subdomain)
                    except Exception:
                        pass
                    
                    # Progress indicator
                    if completed % 10 == 0 or completed == len(self.wordlist):
                        with print_lock:
                            progress = int((completed / len(self.wordlist)) * 100)
                            print(f"{CYAN}  [*]{RESET} Progress: {BRIGHT_GREEN}{progress}%{RESET} ({completed}/{len(self.wordlist)}) | Found: {BRIGHT_GREEN}{len(self.subdomains)}{RESET}")
            
            with print_lock:
                print(f"\n{GREEN}  [+]{RESET} DNS brute-force complete! Found {BRIGHT_GREEN}{len(self.subdomains)}{RESET} subdomains")
            
            return self.subdomains
            
        except Exception as e:
            with print_lock:
                print(f"{RED}  [!]{RESET} Error during DNS brute-force: {str(e)}")
            return self.subdomains
    
    def dns_lookup(self, subdomain: str) -> bool:
        """
        Perform DNS lookup to verify subdomain exists
        Returns True if subdomain resolves
        """
        try:
            # Try A record lookup
            try:
                answers = self.dns_resolver.resolve(subdomain, 'A')
                if answers:
                    with print_lock:
                        print(f"{GREEN}  [✓]{RESET} {BRIGHT_GREEN}{subdomain}{RESET}")
                    return True
            except:
                pass
            
            # Try AAAA record lookup (IPv6)
            try:
                answers = self.dns_resolver.resolve(subdomain, 'AAAA')
                if answers:
                    with print_lock:
                        print(f"{GREEN}  [✓]{RESET} {BRIGHT_GREEN}{subdomain}{RESET}")
                    return True
            except:
                pass
                
            return False
            
        except Exception:
            return False
    
    def deduplicate(self) -> Set[str]:
        """Remove duplicate subdomains"""
        with print_lock:
            print(f"{CYAN}  [*]{RESET} Deduplicating results...")
        unique = set(self.subdomains)
        with print_lock:
            print(f"{GREEN}  [+]{RESET} After deduplication: {BRIGHT_GREEN}{len(unique)}{RESET} unique subdomains")
        return unique
    
    def save_to_json(self, output_path: str):
        """Save subdomains to JSON file"""
        try:
            sorted_subs = sorted(list(self.subdomains))
            
            output_data = {
                "domain": self.domain,
                "timestamp": datetime.now().isoformat(),
                "total_count": len(sorted_subs),
                "enumeration_methods": "crt.sh + DNS brute-force",
                "threads_used": self.threads,
                "subdomains": sorted_subs
            }
            
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            with print_lock:
                print(f"{GREEN}  [+]{RESET} Results saved to: {BRIGHT_GREEN}{output_path}{RESET}")
            return True
            
        except Exception as e:
            with print_lock:
                print(f"{RED}  [!]{RESET} Error saving to JSON: {str(e)}")
            return False
    
    def enumerate(self) -> Set[str]:
        """
        Main enumeration method
        Run all enumeration techniques
        """
        with print_lock:
            print(f"\n{CYAN}{'='*60}{RESET}")
            print(f"{BRIGHT_GREEN}🔍 SUBDOMAIN ENUMERATION STARTED{RESET}")
            print(f"{CYAN}{'='*60}{RESET}\n")
        
        with print_lock:
            print(f"{GREEN}[*] Target: {BRIGHT_GREEN}{self.domain}{RESET}\n")
        
        # Try crt.sh first
        self.query_crt_sh()
        
        # If crt.sh didn't find anything, use DNS brute-force
        if len(self.subdomains) == 0:
            self.dns_brute_force()
        
        # Deduplicate
        self.deduplicate()
        
        with print_lock:
            print(f"\n{CYAN}{'='*60}{RESET}")
            print(f"{GREEN}[✓] Total Subdomains Found: {BRIGHT_GREEN}{len(self.subdomains)}{RESET}")
            print(f"{CYAN}{'='*60}{RESET}\n")
        
        return self.subdomains


def run_enumeration(domain: str, output_file: str = None, threads: int = 10) -> Set[str]:
    """
    Convenience function to run enumeration
    """
    enumerator = SubdomainEnumerator(domain, threads=threads)
    subdomains = enumerator.enumerate()
    
    if output_file:
        enumerator.save_to_json(output_file)
    
    return subdomains