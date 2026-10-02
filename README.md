# RECON-X

**Automated Reconnaissance & Enumeration Tool**  
*Professional subdomain discovery, live host detection, technology fingerprinting, and HTML reporting*

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 What It Does

RECON-X is a complete reconnaissance automation tool designed for offensive security testing and bug bounty hunting. It performs comprehensive subdomain enumeration, detects live hosts, identifies technologies, and generates professional HTML reports.

### Key Features

- 🔍 **Subdomain Enumeration**: Multiple sources (crt.sh, DNS brute-force, zone transfers, reverse DNS)
- ✅ **Live Host Detection**: HTTP/HTTPS probing with status codes and page titles
- 🛠️ **Technology Fingerprinting**: Detects servers, frameworks, CMS, languages
- 📊 **HTML Reporting**: Beautiful, professional reconnaissance reports
- ⚡ **Multi-threaded**: Fast execution with configurable threading
- 📁 **JSON Export**: Structured data for further analysis
- 🎨 **Dark Hacker Theme**: Professional styling with green accent

---

## 📋 Requirements

- Python 3.9+
- pip (Python package manager)
- ~50MB disk space
- Internet connection

### Supported Platforms

- ✅ Windows
- ✅ macOS  
- ✅ Linux

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Gokulpvtr/recon-x.git
cd recon-x
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run RECON-X

```bash
python -m src.main -d example.com -t 10
```

---

## 💻 Usage

### Basic Scan

```bash
python -m src.main -d target.com
```

### With More Threads (Faster)

```bash
python -m src.main -d target.com -t 20
```

### Skip Specific Phases

```bash
# Skip live host probing
python -m src.main -d target.com --no-probe

# Skip technology detection
python -m src.main -d target.com --no-detect

# Skip HTML report generation
python -m src.main -d target.com --no-report
```

### Full Enumeration

```bash
python -m src.main -d target.com --full -t 25
```

---

## 📊 Output Files

After running RECON-X, you'll get:

output/
├── target.com_subdomains.json # All discovered subdomains
├── target.com_live_hosts.json # Live hosts with details
├── target.com_tech_detection.json # Detected technologies
└── target.com_report.html # Professional HTML report


### Open the Report

- **Windows**: Double-click `target.com_report.html`
- **macOS/Linux**: `open output/target.com_report.html`

---

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
target_domain: "example.com"
threads: 10                    # Number of parallel threads
timeout: 5                     # Request timeout in seconds
output_dir: "output"           # Output directory
screenshot: false              # Enable screenshots (future)
full_enum: false               # Full enumeration mode
```

---

## 📈 Typical Results

For a medium-sized domain:

- **Subdomains found**: 50-200
- **Live hosts**: 10-50
- **Execution time**: 2-5 minutes
- **Report size**: 50-200 KB

---

## ⚠️ Legal & Ethics

### Authorization Required

You **MUST** have explicit written permission before using RECON-X on any target. Unauthorized scanning is illegal.

### Responsible Disclosure

If you find vulnerabilities:
1. Document your findings
2. Notify the organization privately
3. Give them 90 days to fix
4. Follow coordinated disclosure guidelines

### Terms of Service

- Only use on domains you own or have authorization for
- Respect rate limits and robots.txt
- Don't disrupt services
- Follow all applicable laws

---

## 🛠️ Enumeration Methods

RECON-X uses multiple techniques:

1. **Certificate Transparency (crt.sh)**: Queries public SSL certificate logs
2. **DNS Brute-force**: Tests common subdomain names with wordlist
3. **Zone Transfers**: Attempts AXFR queries (usually blocked)
4. **Reverse DNS**: Looks up PTR records
5. **Live Probing**: Tests HTTP/HTTPS on discovered subdomains
6. **Header Analysis**: Detects server software
7. **Content Analysis**: Identifies frameworks and CMS

---

## 🎓 Learning Resources

- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [HackerOne Reports](https://hackerone.com/reports)
- [Bug Bounty Programs](https://bugcrowd.com)

---

## 📝 Project Structure

recon-x/
├── src/
│ ├── init.py
│ ├── main.py # Entry point
│ ├── enumerator.py # Subdomain enumeration
│ ├── prober.py # Live host probing
│ ├── detector.py # Technology fingerprinting
│ └── reporter.py # HTML report generation
├── wordlists/
│ └── subdomains.txt # Common subdomain names
├── output/ # Generated reports (created at runtime)
├── config.yaml # Configuration file
├── requirements.txt # Python dependencies
├── README.md # This file
├── TESTING.md # Testing guide
└── .gitignore # Git ignore rules


---

## 🐛 Troubleshooting

### No subdomains found
- Verify domain is correct
- Check internet connection
- Try without DNS verification: `--no-dns`

### "ModuleNotFoundError: No module named 'src'"
- Run from project root: `cd recon-x`
- Use: `python -m src.main`

### Slow execution
- Increase threads: `-t 25`
- Use less restrictive timeout: Edit config.yaml

### crt.sh API errors
- Tool automatically falls back to DNS brute-force
- No action needed

### Permission denied on output files
- Check folder permissions
- Ensure write access to `output/` folder

---

## 🚀 Next Steps

After reconnaissance:

1. **Analyze Results**: Review the HTML report
2. **Prioritize**: Focus on live hosts with interesting tech
3. **Enumerate Further**: 
   - Scan for common ports (nmap)
   - Test for known vulnerabilities
   - Check security headers
4. **Test Vulnerabilities**: Use Burp Suite, OWASP ZAP
5. **Document Findings**: Create professional report
6. **Responsible Disclosure**: Report vulnerabilities properly

---

## 🤝 Contributing

Found a bug? Have suggestions? 

1. Test the issue thoroughly
2. Create a detailed description
3. Open an issue on GitHub
4. Submit a pull request with fix

---

## 📚 Resources

### Tools to Complement RECON-X

- **Burp Suite**: Web application testing
- **OWASP ZAP**: Vulnerability scanning
- **Nmap**: Port scanning
- **Nikto**: Web server scanning
- **Shodan**: Device search engine

### Further Learning

- **HackerOne**: Active bug bounty programs
- **Bugcrowd**: Organized vulnerability research
- **OWASP**: Web security standards
- **SANS**: Cybersecurity training

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Gokulkrishnan S**
- **GitHub**: [@Gokulpvtr](https://github.com/Gokulpvtr)
- **Interest**: Offensive Security & Bug Bounty
- **Location**: Kerala, India
- **Education**: Final-year BCA, University of Kerala

---

## 🎓 Skills Used

- Python programming
- Network security
- DNS enumeration
- HTTP protocol
- Multi-threading
- JSON/HTML
- Git & GitHub
- Linux/Windows

---

## ⭐ Show Your Support

If RECON-X helped you:
- ⭐ Star the repository
- 🔗 Share it with others
- 💬 Provide feedback
- 🐛 Report bugs
- 🚀 Contribute improvements

---

**Happy hunting! 🎯**