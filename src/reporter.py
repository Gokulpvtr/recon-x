#!/usr/bin/env python3
"""
RECON-X Report Generation Module
Creates beautiful HTML reports from reconnaissance data
"""

import json
from datetime import datetime
from typing import Dict, Set
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

class ReportGenerator:
    def __init__(self, domain: str, subdomains: Set[str], live_hosts: Dict, tech_data: Dict = None):
        """Initialize report generator"""
        self.domain = domain
        self.subdomains = subdomains
        self.live_hosts = live_hosts
        self.tech_data = tech_data or {}
    
    def generate_html(self) -> str:
        """Generate HTML report"""
        
        # Calculate statistics
        total_subs = len(self.subdomains)
        total_live = len(self.live_hosts)
        responsiveness = (total_live / max(total_subs, 1)) * 100
        
        # Get technology summary
        servers = {}
        cms_list = []
        languages = []
        frameworks = []
        
        for subdomain, tech_info in self.tech_data.items():
            if tech_info.get("server"):
                server = tech_info["server"].split('/')[0]
                servers[server] = servers.get(server, 0) + 1
            if tech_info.get("cms"):
                if tech_info["cms"] not in cms_list:
                    cms_list.append(tech_info["cms"])
            if tech_info.get("language"):
                if tech_info["language"] not in languages:
                    languages.append(tech_info["language"])
            for tech in tech_info.get("detected_tech", []):
                if tech not in frameworks and tech not in cms_list and tech not in languages:
                    if tech not in frameworks:
                        frameworks.append(tech)
        
        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RECON-X Report - {self.domain}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
            color: #e0e0e0;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(20, 20, 40, 0.9);
            border-radius: 10px;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.1);
            border: 1px solid rgba(0, 255, 0, 0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
            color: #000;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
            border-left: 4px solid #00ff00;
            padding-left: 20px;
        }}
        
        .section h2 {{
            color: #00ff00;
            font-size: 1.8em;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-box {{
            background: rgba(0, 255, 0, 0.05);
            border: 2px solid #00ff00;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            color: #00ff00;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            color: #aaa;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 1px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th {{
            background: rgba(0, 255, 0, 0.1);
            color: #00ff00;
            padding: 15px;
            text-align: left;
            border-bottom: 2px solid #00ff00;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 1px;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(0, 255, 0, 0.1);
        }}
        
        tr:hover {{
            background: rgba(0, 255, 0, 0.05);
        }}
        
        .status-200 {{ color: #00ff00; font-weight: bold; }}
        .status-301 {{ color: #ffaa00; }}
        .status-400 {{ color: #ff6600; }}
        .status-403 {{ color: #ff4444; }}
        .status-404 {{ color: #ff4444; }}
        .status-500 {{ color: #ff0000; }}
        
        .tech-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }}
        
        .tech-badge {{
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .footer {{
            background: rgba(0, 0, 0, 0.5);
            color: #999;
            padding: 20px;
            text-align: center;
            border-top: 1px solid rgba(0, 255, 0, 0.2);
            font-size: 0.9em;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .summary-item {{
            background: rgba(0, 255, 0, 0.05);
            border-left: 3px solid #00ff00;
            padding: 15px;
            border-radius: 5px;
        }}
        
        .summary-item strong {{
            color: #00ff00;
        }}
        
        .code {{
            background: rgba(0, 0, 0, 0.3);
            border-left: 3px solid #00ff00;
            padding: 10px;
            margin: 5px 0;
            font-family: 'Courier New', monospace;
            color: #00ff00;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 RECON-X RECONNAISSANCE REPORT</h1>
            <p>Automated Security Assessment for {self.domain}</p>
            <p style="font-size: 0.9em; margin-top: 15px;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <!-- EXECUTIVE SUMMARY -->
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{total_subs}</div>
                        <div class="stat-label">Total Subdomains</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{total_live}</div>
                        <div class="stat-label">Live Hosts</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{responsiveness:.1f}%</div>
                        <div class="stat-label">Responsiveness</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{len(servers)}</div>
                        <div class="stat-label">Web Servers</div>
                    </div>
                </div>
            </div>
            
            <!-- TECHNOLOGIES DETECTED -->
            <div class="section">
                <h2>🛠️ Technologies Detected</h2>
                
                <div class="summary-grid">
"""
        
        # Add detected technologies
        if servers:
            html += "<div class='summary-item'><strong>Web Servers:</strong><br>"
            for server, count in sorted(servers.items(), key=lambda x: x[1], reverse=True):
                html += f"  • {server} ({count})<br>"
            html += "</div>"
        
        if cms_list:
            html += "<div class='summary-item'><strong>CMS Platforms:</strong><br>"
            for cms in cms_list:
                html += f"  • {cms}<br>"
            html += "</div>"
        
        if languages:
            html += "<div class='summary-item'><strong>Languages:</strong><br>"
            for lang in languages:
                html += f"  • {lang}<br>"
            html += "</div>"
        
        if frameworks:
            html += "<div class='summary-item'><strong>Frameworks:</strong><br>"
            for fw in frameworks[:5]:
                html += f"  • {fw}<br>"
            html += "</div>"
        
        html += """
                </div>
            </div>
            
            <!-- LIVE HOSTS -->
            <div class="section">
                <h2>🌐 Live Hosts Discovered</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Subdomain</th>
                            <th>Status</th>
                            <th>Title</th>
                            <th>Server</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Add live hosts
        for subdomain, host_info in sorted(self.live_hosts.items()):
            status = host_info.get('https_status') or host_info.get('http_status') or 'N/A'
            title = host_info.get('https_title') or host_info.get('http_title') or 'N/A'
            server = host_info.get('server', 'N/A')
            
            status_class = f"status-{status}" if isinstance(status, int) else "status-200"
            
            html += f"""
                        <tr>
                            <td><code>{subdomain}</code></td>
                            <td class="{status_class}">{status}</td>
                            <td>{title}</td>
                            <td>{server}</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <!-- ALL SUBDOMAINS -->
            <div class="section">
                <h2>📝 All Discovered Subdomains</h2>
                <div class="code">
"""
        
        # Add all subdomains
        for subdomain in sorted(self.subdomains):
            html += f"{subdomain}<br>"
        
        html += """
                </div>
            </div>
            
            <!-- RECOMMENDATIONS -->
            <div class="section">
                <h2>💡 Recommendations</h2>
                <div class="summary-grid">
                    <div class="summary-item">
                        <strong>Next Steps:</strong><br>
                        • Investigate live hosts for vulnerabilities<br>
                        • Check for default credentials<br>
                        • Test for common misconfigurations<br>
                        • Review security headers<br>
                        • Perform penetration testing
                    </div>
                    <div class="summary-item">
                        <strong>Security Notes:</strong><br>
                        • Ensure authorization before testing<br>
                        • Document all findings<br>
                        • Follow responsible disclosure<br>
                        • Respect rate limits<br>
                        • Use VPN if appropriate
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>RECON-X v1.0 | Automated Reconnaissance Tool | Owner: Gokulkrishnan S</p>
            <p>This report was generated for authorized security testing purposes only.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def save_html(self, output_path: str) -> bool:
        """Save HTML report to file"""
        try:
            html = self.generate_html()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            with print_lock:
                print(f"{GREEN}  [+]{RESET} HTML Report saved to: {BRIGHT_GREEN}{output_path}{RESET}")
            
            return True
            
        except Exception as e:
            with print_lock:
                print(f"{RED}  [!]{RESET} Error saving HTML report: {str(e)}")
            return False


def generate_report(domain: str, subdomains: Set[str], live_hosts: Dict, tech_data: Dict = None, output_file: str = None) -> bool:
    """
    Convenience function to generate report
    """
    generator = ReportGenerator(domain, subdomains, live_hosts, tech_data)
    
    if output_file:
        return generator.save_html(output_file)
    
    return True