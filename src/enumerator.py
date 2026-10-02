#!/usr/bin/env python3
"""
RECON-X Subdomain Enumeration Module
Advanced methods: crt.sh, DNS brute-force, reverse DNS, zone transfers
Uses threading for faster enumeration
"""

import requests
import json
import sys
import dns.resolver
import dns.rdatatype
import dns.zone
import dns.query
from datetime import datetime
from typing import Set, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import socket

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
        self.nameservers = []
        
    def load_wordlist(self) -> List[str]:
        """Load subdomains from wordlist"""
        try:
            with open('wordlists/subdomains.txt', 'r') as f:
                return [line.strip().lower() for line in f if line.strip()]
        except FileNotFoundError:
            with print_lock:
                print(f"{YELLOW}  [!]{RESET} Wordlist not found, using basic list")
            return ['www', 'mail', 'ftp', 'smtp', 'api', 'admin', 'test', 'dev', 'staging', 'cdn', 'static', 'blog', 'shop', 'app', 'apps', 'server', 'db', 'database', 'backup', 'git', 'svn']
    
    def get_nameservers(self) -> List[str]:
        """Get nameservers for the domain"""
        try:
            with print_lock:
                print(f"{CYAN}  [*]{RESET} Fetching nameservers for {BRIGHT_GREEN}{self.domain}{RESET}...")
            
            nameservers = []
            answers = dns.resolver.resolve(self.domain, 'NS')
            
            for rdata in answers:
                ns = str(rdata.target).rstrip('.')
                nameservers.append(ns)
            
            with print_lock:
                print(f"{GREEN}  [+]{RESET} Found {BRIGHT_GREEN}{len(nameservers)}{RESET} nameservers")
                for ns in nameservers[:3]:
                    print(f"{GREEN}     └─{RESET} {BRIGHT_GREEN}{ns}{RESET}")
            
            return nameservers
            
        except Exception as e:
            with print_lock:
                print(f"{YELLOW}  [!]{RESET} Could not get nameservers: {str(e)}")
            return []
    
    def zone_transfer_attempt(self, nameserver: str) -> Set[str]:
        """
        Attempt DNS zone transfer (AXFR) on nameserver
        This is a legitimate technique if authorized
        """
        try:
            zone_subs = set()
            
            zone = dns.zone.from_xfr(dns.query.xfr(nameserver, self.domain))
            
            for name, node in zone.items():
                subdomain = str(name).rstrip('.')
                if subdomain == '@':
                    subdomain = self.domain
                else:
                    subdomain = f"{subdomain}.{self.domain}"
                
                zone_subs.add(subdomain)
            
            with print_lock:
                print(f"{GREEN}  [+]{RESET} Zone transfer successful on {BRIGHT_GREEN}{nameserver}{RESET}! Found {BRIGHT_GREEN}{len(zone_subs)}{RESET} subdomains")
            
            return zone_subs
            
        except Exception:
            return set()
    
    def reverse_dns_lookup(self, ip: str) -> Set[str]:
        """
        Perform reverse DNS lookup on IP address
        Returns hostnames associated with IP
        """
        try:
            reverse_names = set()
            reverse_ip = dns.reversename.from_address(ip)
            
            try:
                answers = dns.resolver.resolve(reverse_ip, 'PTR')
                for rdata in answers:
                    hostname = str(rdata).rstrip('.')
                    if self.domain in hostname:
                        reverse_names.add(hostname)
            except:
                pass
            
            return reverse_names
            
        except Exception:
            return set()
    
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
                        print(f"{YELLOW}  [!]{RESET} crt.sh is down (502). Retrying in {retry_delay}s...")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    continue
                else:
                    with print_lock:
                        print(f"{YELLOW}  [!]{RESET} crt.sh returned status code {response.status_code}")
                    
            except requests.exceptions.Timeout:
                with print_lock:
                    print(f"{YELLOW}  [!]{RESET} crt.sh request timed out")
                
            except requests.exceptions.RequestException as e:
                with print_lock:
                    print(f"{YELLOW}  [!]{RESET} Error querying crt.sh: {str(e)}")
        
        with print_lock:
            print(f"{YELLOW}  [!]{RESET} crt.sh unavailable, using fallback methods")
        return self.subdomains
    
    def dns_brute_force(self) -> Set[str]:
        """
        DNS brute-force enumeration using wordlist
        Tests common subdomain names with threading
        """
        try:
            with print_lock:
                print(f"\n{CYAN}  [*]{RESET} Starting DNS brute-force with {BRIGHT_GREEN}{self.threads}{RESET} threads...")
                print(f"{CYAN}  [*]{RESET} Testing {BRIGHT_GREEN}{len(self.wordlist)}{RESET} subdomains...\n")
            
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {}
                for word in self.wordlist:
                    subdomain = f"{word}.{self.domain}"
                    future = executor.submit(self.dns_lookup, subdomain)
                    futures[future] = subdomain
                
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
            try:
                answers = self.dns_resolver.resolve(subdomain, 'A')
                if answers:
                    with print_lock:
                        print(f"{GREEN}  [✓]{RESET} {BRIGHT_GREEN}{subdomain}{RESET}")
                    return True
            except:
                pass
            
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
                "enumeration_methods": [
                    "crt.sh (Certificate Transparency)",
                    "DNS brute-force",
                    "Zone transfer attempts",
                    "Reverse DNS lookups"
                ],
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
        
        # Method 1: crt.sh
        with print_lock:
            print(f"{YELLOW}[→] METHOD 1: Certificate Transparency (crt.sh){RESET}")
        self.query_crt_sh()
        
        # Method 2: DNS Brute-force
        with print_lock:
            print(f"\n{YELLOW}[→] METHOD 2: DNS Brute-Force{RESET}")
        if len(self.subdomains) == 0:
            self.dns_brute_force()
        else:
            with print_lock:
                print(f"{CYAN}  [*]{RESET} Skipping brute-force (found {len(self.subdomains)} from crt.sh)")
        
        # Method 3: Zone Transfer
        with print_lock:
            print(f"\n{YELLOW}[→] METHOD 3: Zone Transfer Attempts{RESET}")
        nameservers = self.get_nameservers()
        zone_subs = set()
        
        for ns in nameservers[:2]:  # Try first 2 nameservers
            try:
                found = self.zone_transfer_attempt(ns)
                zone_subs.update(found)
                self.subdomains.update(found)
            except:
                with print_lock:
                    print(f"{YELLOW}  [!]{RESET} Zone transfer failed on {ns} (likely denied)")
        
        if not zone_subs:
            with print_lock:
                print(f"{YELLOW}  [!]{RESET} Zone transfers denied (expected on most servers)")
        
        # Deduplicate
        with print_lock:
            print(f"\n{YELLOW}[→] Finalizing Results{RESET}\n")
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