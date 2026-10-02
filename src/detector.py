#!/usr/bin/env python3
"""
RECON-X Tech Fingerprinting Module
Detects servers, frameworks, CMS, technologies
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, Set, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Colors
BRIGHT_GREEN = '\033[1;92m'
CYAN = '\033[1;96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

# Thread lock for safe printing
print_lock = threading.Lock()

class TechDetector:
    def __init__(self, live_hosts: Dict, timeout: int = 5, threads: int = 10):
        """Initialize detector with live hosts"""
        self.live_hosts = live_hosts
        self.timeout = timeout
        self.threads = threads
        self.tech_data = {}
        
        # Technology signatures
        self.signatures = {
            "servers": {
                "nginx": [r"nginx", r"nginx/"],
                "Apache": [r"Apache", r"Apache/"],
                "IIS": [r"IIS", r"Microsoft-IIS"],
                "CloudFlare": [r"cloudflare"],
                "LiteSpeed": [r"LiteSpeed"],
            },
            "frameworks": {
                "Django": [r"Django", r"django"],
                "React": [r"react", r"React"],
                "Vue": [r"vue", r"Vue"],
                "Angular": [r"angular", r"Angular"],
                "Express": [r"express", r"Express"],
                "Spring": [r"Spring", r"spring"],
                "Laravel": [r"Laravel", r"laravel"],
                "WordPress": [r"WordPress", r"wordpress"],
                "Drupal": [r"Drupal", r"drupal"],
            },
            "cms": {
                "WordPress": [r"wp-content", r"wp-includes", r"WordPress"],
                "Drupal": [r"drupal", r"/sites/", r"Drupal"],
                "Joomla": [r"Joomla", r"joomla", r"/components/"],
                "Magento": [r"magento", r"Magento"],
                "Shopify": [r"Shopify", r"shopify", r"myshopify"],
                "Wix": [r"wix", r"Wix"],
                "Squarespace": [r"squarespace", r"Squarespace"],
            },
            "javascript": {
                "jQuery": [r"jquery"],
                "Bootstrap": [r"bootstrap"],
                "Material": [r"material"],
                "Tailwind": [r"tailwind"],
            },
            "languages": {
                "PHP": [r"php", r"PHP"],
                "Python": [r"python", r"Python"],
                "Java": [r"java", r"Java"],
                "Node.js": [r"node", r"Node"],
                "Ruby": [r"ruby", r"Ruby"],
            }
        }
    
    def detect_from_headers(self, headers: Dict) -> Dict:
        """
        Detect technology from HTTP headers
        """
        detected = {
            "server": None,
            "powered_by": None,
            "x_aspnet": None,
            "x_powered_by": None,
        }
        
        # Check common header fields
        if "Server" in headers:
            detected["server"] = headers["Server"]
        
        if "X-Powered-By" in headers:
            detected["x_powered_by"] = headers["X-Powered-By"]
        
        if "X-AspNet-Version" in headers:
            detected["x_aspnet"] = headers["X-AspNet-Version"]
        
        return detected
    
    def detect_from_content(self, html: str) -> List[str]:
        """
        Detect technology from HTML content
        """
        detected = []
        
        for category, techs in self.signatures.items():
            for tech, patterns in techs.items():
                for pattern in patterns:
                    if re.search(pattern, html, re.IGNORECASE):
                        if tech not in detected:
                            detected.append(tech)
                        break
        
        return detected
    
    def detect_subdomain(self, subdomain: str, host_info: Dict) -> Dict:
        """
        Detect tech for a single subdomain
        """
        tech_info = {
            "subdomain": subdomain,
            "server": None,
            "headers": {},
            "detected_tech": [],
            "cms": None,
            "language": None,
        }
        
        # Try HTTPS first
        url = None
        response = None
        
        for protocol in ["https", "http"]:
            try:
                url = f"{protocol}://{subdomain}"
                response = requests.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    verify=False,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                
                if response.status_code < 400:
                    break
                    
            except:
                continue
        
        if not response:
            return tech_info
        
        try:
            # Get headers
            headers_dict = dict(response.headers)
            tech_info["headers"] = headers_dict
            
            # Detect from headers
            header_tech = self.detect_from_headers(headers_dict)
            if header_tech["server"]:
                tech_info["server"] = header_tech["server"]
            
            # Detect from content
            detected = self.detect_from_content(response.text[:50000])  # First 50KB
            tech_info["detected_tech"] = detected
            
            # Categorize findings
            for tech in detected:
                # Check if CMS
                for cms_name in self.signatures["cms"]:
                    if tech.lower() == cms_name.lower():
                        tech_info["cms"] = tech
                
                # Check if language
                for lang_name in self.signatures["languages"]:
                    if tech.lower() == lang_name.lower():
                        tech_info["language"] = tech
            
            with print_lock:
                tech_str = ", ".join(detected) if detected else "None"
                server_str = tech_info["server"] if tech_info["server"] else "Unknown"
                print(f"{GREEN}  [+]{RESET} {BRIGHT_GREEN}{subdomain}{RESET}")
                print(f"      Server: {server_str}")
                print(f"      Tech: {tech_str}")
            
            return tech_info
            
        except Exception as e:
            return tech_info
    
    def detect_all_threaded(self) -> Dict:
        """
        Detect tech for all live hosts with threading
        """
        try:
            with print_lock:
                print(f"\n{CYAN}  [*]{RESET} Starting tech detection with {BRIGHT_GREEN}{self.threads}{RESET} threads...")
                print(f"{CYAN}  [*]{RESET} Analyzing {BRIGHT_GREEN}{len(self.live_hosts)}{RESET} hosts...\n")
            
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {
                    executor.submit(self.detect_subdomain, subdomain, host_info): subdomain 
                    for subdomain, host_info in self.live_hosts.items()
                }
                
                completed = 0
                
                for future in as_completed(futures):
                    subdomain = futures[future]
                    completed += 1
                    
                    try:
                        result = future.result()
                        self.tech_data[subdomain] = result
                    except Exception as e:
                        pass
                    
                    # Progress indicator
                    if completed % 5 == 0 or completed == len(self.live_hosts):
                        with print_lock:
                            progress = int((completed / len(self.live_hosts)) * 100)
                            print(f"{CYAN}  [*]{RESET} Progress: {BRIGHT_GREEN}{progress}%{RESET} ({completed}/{len(self.live_hosts)})")
            
            with print_lock:
                print(f"\n{GREEN}  [+]{RESET} Tech detection complete!\n")
            
            return self.tech_data
            
        except Exception as e:
            with print_lock:
                print(f"{RED}  [!]{RESET} Error during detection: {str(e)}")
            return self.tech_data
    
    def get_summary(self) -> Dict:
        """Get summary of detected technologies"""
        summary = {
            "total_analyzed": len(self.tech_data),
            "servers": {},
            "cms_found": [],
            "languages": [],
            "frameworks": [],
        }
        
        for subdomain, tech_info in self.tech_data.items():
            # Count servers
            if tech_info["server"]:
                server = tech_info["server"].split('/')[0]
                summary["servers"][server] = summary["servers"].get(server, 0) + 1
            
            # Collect CMS
            if tech_info["cms"]:
                if tech_info["cms"] not in summary["cms_found"]:
                    summary["cms_found"].append(tech_info["cms"])
            
            # Collect languages
            if tech_info["language"]:
                if tech_info["language"] not in summary["languages"]:
                    summary["languages"].append(tech_info["language"])
            
            # Collect frameworks
            for tech in tech_info["detected_tech"]:
                if tech not in summary["frameworks"] and tech not in summary["cms_found"] and tech not in summary["languages"]:
                    summary["frameworks"].append(tech)
        
        return summary
    
    def save_to_json(self, output_path: str):
        """Save tech detection results to JSON file"""
        try:
            summary = self.get_summary()
            
            output_data = {
                "timestamp": datetime.now().isoformat(),
                "total_hosts_analyzed": len(self.tech_data),
                "summary": summary,
                "detailed_results": self.tech_data
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


def run_detection(live_hosts: Dict, output_file: str = None, threads: int = 10) -> Dict:
    """
    Convenience function to run detection
    """
    detector = TechDetector(live_hosts, threads=threads)
    tech_data = detector.detect_all_threaded()
    
    if output_file:
        detector.save_to_json(output_file)
    
    return tech_data, detector.get_summary()