# RECON-X Testing Guide

## Quick Test Suite

### Test 1: Basic Enumeration
```bash
python -m src.main -d google.com -t 10
```
Expected: Should find subdomains and generate all outputs

### Test 2: Skip Probing
```bash
python -m src.main -d github.com -t 10 --no-probe
```
Expected: Only enumeration, no probing

### Test 3: Skip Detection
```bash
python -m src.main -d amazon.com -t 10 --no-detect
```
Expected: Enumeration + probing only

### Test 4: Skip Report
```bash
python -m src.main -d microsoft.com -t 10 --no-report
```
Expected: No HTML report generated

### Test 5: High Threads
```bash
python -m src.main -d cloudflare.com -t 25
```
Expected: Faster execution

### Test 6: Small Domain
```bash
python -m src.main -d example.com -t 10
```
Expected: Should work even with few results

## Output Files Check

After each test, verify:
```bash
ls -la output/
cat output/[domain]_subdomains.json
cat output/[domain]_live_hosts.json
cat output/[domain]_tech_detection.json
# Open HTML in browser
```

## Expected Results

- ✅ JSON files with valid formatting
- ✅ HTML report opens without errors
- ✅ All subdomains listed
- ✅ Live hosts marked correctly
- ✅ Technologies detected
- ✅ No crashes or exceptions

## Known Limitations

- Zone transfers usually fail (expected on most servers)
- Some domains may timeout
- Large wordlists may take time
- Rate limiting may occur on some targets

## Troubleshooting

### No subdomains found
- Check internet connection
- Verify domain exists
- Try --no-dns flag

### crt.sh API down
- Tool uses DNS brute-force as fallback
- Should continue automatically

### High memory usage
- Reduce thread count: `-t 5`
- Smaller domains use less memory

### Slow execution
- Increase threads: `-t 25`
- Skip DNS verification: `--no-dns`