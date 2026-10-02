# RECON-X

**Automated Reconnaissance & Enumeration Tool**  
*Subdomain discovery, live host detection, tech fingerprinting, and reporting*

**Owner:** Gokulkrishnan S  
**GitHub:** [@Gokulpvtr](https://github.com/Gokulpvtr)  
**Status:** In Development (15-Day Challenge)

---

## What It Does

- 🔍 **Subdomain Enumeration**: Passive and active discovery via crt.sh, DNS queries
- ✅ **Live Host Detection**: HTTP/HTTPS probing with status codes and response times
- 🛠️ **Tech Fingerprinting**: Server, framework, and CMS detection from headers
- 📸 **Screenshots**: Visual capture of live domains
- 📊 **HTML Reporting**: Clean, readable reports with findings and statistics

---

## Installation

### Requirements
- Python 3.9+
- pip

### Setup

```bash
git clone https://github.com/Gokulpvtr/recon-x.git
cd recon-x
pip install -r requirements.txt
```

### Configuration

Edit `config.yaml`:
```yaml
target_domain: "example.com"
threads: 10
timeout: 5
screenshot: true
```

---

## Usage

```bash
python src/main.py -d example.com
python src/main.py -d example.com --full
python src/main.py -d example.com --screenshot
```

### Output
- `output/example.com_subdomains.json` — All discovered subdomains
- `output/example.com_report.html` — Full reconnaissance report
- `output/screenshots/` — Domain screenshots

---

## Features

- [x] Project Setup & Banner
- [x] Subdomain Enumeration (Days 2-5)
- [ ] Live Host Detection (Days 6-8)
- [ ] Tech Fingerprinting (Days 9-10)
- [ ] Report Generation (Days 11-12)
- [ ] Testing & Polish (Days 13-15)

---

## Legal & Ethics

⚠️ **Authorization Required**: Only run this tool on domains you own or have explicit written permission to test. Unauthorized scanning is illegal.

---

## Author

**Gokulkrishnan S**  
- GitHub: [@Gokulpvtr](https://github.com/Gokulpvtr)
- Interest: Bug Bounty Hunting & Offensive Security

---

## License

MIT