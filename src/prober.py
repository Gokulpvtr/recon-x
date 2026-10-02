#!/usr/bin/env python3
"""
RECON-X Live Host Probing Module
Tests subdomains for HTTP/HTTPS, status codes, titles, headers
Uses threading for speed
"""

import requests
import json
from datetime import datetime
from typing import Dict, Set, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from urllib.parse import urlparse
import re

# Colors
BRIGHT_GREEN = '\033[1;92m'
CYAN = '\033[1;96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

# Thread lock for safe printing
print_lock = threading.Lock()

class LiveHostProber:
    def __init__(self, subdomains: Set[str], timeout: int = 5, threads: int = 10):
        """Initialize prober with subdomains"""
        self.subdomains = subdomains
        self.timeout = timeout
        self.threads = threads
        self.live_hosts = {}  # {subdomain: {status, title, server, etc}}
        
    def extract_title(self, html: str) -> str:
        """Extract title from HTML response"""
        try:
            match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:100]  # Limit to 100 chars
            return "N/A"
        except:
            return "N/A"
    
    def probe_subdomain(self, subdomain: str) -> Dict:
        """
        Probe a single subdomain for HTTP/HTTPS
        Returns dict with results
        """
        result = {
            "subdomain": subdomain,
            "http_status": None,
            "https_status": None,
            "http_title": None,
            "https_title": None,
            "server": None,
            "content_type": None,
            "content_length": None,
            "is_live": False
        }
        
        # Try HTTPS first
        try:
            url = f"https://{subdomain}"
            response = requests.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=False,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            result["https_status"] = response.status_code
            result["server"] = response.headers.get('Server', 'N/A')
            result["content_type"] = response.headers.get('Content-Type', 'N/A')
            result["content_length"] = response.headers.get('Content-Length', 'N/A')
            result["https_title"] = self.extract_title(response.text)
            result["is_live"] = True
            
            with print_lock:
                status_color = GREEN if 200 <= response.status_code < 400 else YELLOW if 400 <= response.status_code < 500 else RED
                print(f"{status_color}  [HTTPS] {response.status_code}{RESET} | {BRIGHT_GREEN}{subdomain}{RESET} | {result['https_title']}")
            
            return result
            
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.SSLError:
            # SSL error, try HTTP
            pass
        except Exception as e:
            pass
        
        # Try HTTP as fallback
        try:
            url = f"http://{subdomain}"
            response = requests.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            result["http_status"] = response.status_code
            result["server"] = response.headers.get('Server', 'N/A')
            result["content_type"] = response.headers.get('Content-Type', 'N/A')
            result["content_length"] = response.headers.get('Content-Length', 'N/A')
            result["http_title"] = self.extract_title(response.text)
            result["is_live"] = True
            
            with print_lock:
                status_color = GREEN if 200 <= response.status_code < 400 else YELLOW if 400 <= response.status_code < 500 else RED
                print(f"{status_color}  [HTTP]  {response.status_code}{RESET} | {BRIGHT_GREEN}{subdomain}{RESET} | {result['http_title']}")
            
            return result
            
        except requests.exceptions.Timeout:
            with print_lock:
                print(f"{YELLOW}  [TIMEOUT]{RESET} | {subdomain}")
        except requests.exceptions.ConnectionError:
            with print_lock:
                print(f"{RED}  [OFFLINE]{RESET} | {subdomain}")
        except Exception as e:
            pass
        
        return result
    
    def probe_all_threaded(self) -> Dict:
        """
        Probe all subdomains with threading
        Returns dict of all results
        """
        try:
            with print_lock:
                print(f"\n{CYAN}  [*]{RESET} Starting live host probing with {BRIGHT_GREEN}{self.threads}{RESET} threads...")
                print(f"{CYAN}  [*]{RESET} Testing {BRIGHT_GREEN}{len(self.subdomains)}{RESET} hosts...\n")
            
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {
                    executor.submit(self.probe_subdomain, subdomain): subdomain 
                    for subdomain in self.subdomains
                }
                
                completed = 0
                live_count = 0
                
                for future in as_completed(futures):
                    subdomain = futures[future]
                    completed += 1
                    
                    try:
                        result = future.result()
                        if result["is_live"]:
                            self.live_hosts[subdomain] = result
                            live_count += 1
                    except Exception as e:
                        pass
                    
                    # Progress indicator
                    if completed % 10 == 0 or completed == len(self.subdomains):
                        with print_lock:
                            progress = int((completed / len(self.subdomains)) * 100)
                            print(f"{CYAN}  [*]{RESET} Progress: {BRIGHT_GREEN}{progress}%{RESET} ({completed}/{len(self.subdomains)}) | Live: {BRIGHT_GREEN}{live_count}{RESET}")
            
            with print_lock:
                print(f"\n{GREEN}  [+]{RESET} Probing complete! Found {BRIGHT_GREEN}{len(self.live_hosts)}{RESET} live hosts\n")
            
            return self.live_hosts
            
        except Exception as e:
            with print_lock:
                print(f"{RED}  [!]{RESET} Error during probing: {str(e)}")
            return self.live_hosts
    
    def save_to_json(self, output_path: str):
        """Save live hosts to JSON file"""
        try:
            output_data = {
                "domain": "multiple",
                "timestamp": datetime.now().isoformat(),
                "total_tested": len(self.subdomains),
                "total_live": len(self.live_hosts),
                "live_hosts": self.live_hosts
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


def run_probing(subdomains: Set[str], output_file: str = None, threads: int = 10) -> Dict:
    """
    Convenience function to run probing
    """
    prober = LiveHostProber(subdomains, threads=threads)
    live_hosts = prober.probe_all_threaded()
    
    if output_file:
        prober.save_to_json(output_file)
    
    return live_hosts