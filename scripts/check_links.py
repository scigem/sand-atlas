#!/usr/bin/env python3
"""
Sand Atlas Link Checker

A comprehensive tool to check links in the Sand Atlas website, with special attention to
hosted data links (data.scigem-eng.sydney.edu.au) and future-proofing for changes to 
the dropdown structure.

This script can be used both locally for development and in CI/CD pipelines.

Usage:
    python3 scripts/check_links.py [options]

Options:
    --site-dir DIR      Directory containing built Jekyll site (default: _site)
    --quick             Quick check (sample links only)
    --hosted-only       Check only hosted data links
    --output FORMAT     Output format: json, markdown, both (default: both)
    --ci-mode           Enable CI mode (optimized for GitHub Actions)
    --max-sand-types N  Limit number of sand types to check (default: all)
"""

import os
import re
import json
import argparse
import urllib.parse
from pathlib import Path
from collections import defaultdict
import time
import sys
import subprocess

# Try to import requests, but make it optional
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️ requests library not available - some features will be disabled")
    print("💡 Install with: pip install requests")

class SandAtlasLinkChecker:
    def __init__(self, site_dir="_site", quick_mode=False, ci_mode=False, max_sand_types=None):
        self.site_dir = Path(site_dir)
        self.quick_mode = quick_mode
        self.ci_mode = ci_mode
        self.max_sand_types = max_sand_types
        self.results = {
            "hosted_data_links": {
                "working": [],
                "broken": [],
                "patterns": [],
                "sample_urls": []
            },
            "external_links": {
                "working": [],
                "broken": []
            },
            "internal_links": {
                "working": [],
                "broken": []
            },
            "metadata": {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                "quick_mode": quick_mode,
                "ci_mode": ci_mode,
                "max_sand_types": max_sand_types,
                "patterns_checked": []
            },
            "summary": {}
        }
        
        # Define hosted data patterns - future-proof design
        self.hosted_data_patterns = [
            r'https://data\.scigem-eng\.sydney\.edu\.au/sand-atlas/',
            r'\{\{\s*include\.sand\s*\}\}',  # Jekyll template pattern
            # Add more patterns here as hosting changes
        ]
        
    def find_dropdown_patterns(self):
        """
        Find and extract download link patterns from dropdown.html and other templates.
        This makes the checker future-proof for changes to the dropdown structure.
        """
        patterns_found = set()
        sample_urls = []
        
        # Check dropdown.html specifically
        dropdown_file = Path("_includes/dropdown.html")
        if dropdown_file.exists():
            print(f"📋 Analyzing dropdown patterns in {dropdown_file}")
            
            try:
                with open(dropdown_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all data.scigem-eng links
                data_links = re.findall(
                    r'href=["\']([^"\']*data\.scigem-eng\.sydney\.edu\.au/sand-atlas[^"\']*)["\']',
                    content
                )
                
                for link in data_links:
                    # Extract the base pattern
                    pattern = re.sub(
                        r'\{\{\s*include\.[^}]+\}\}',
                        '{SAND_ID}',
                        link
                    )
                    patterns_found.add(pattern)
                    sample_urls.append(link)
                    
            except Exception as e:
                print(f"❌ Error reading {dropdown_file}: {e}")
        
        # Check other include files for data links
        includes_dir = Path("_includes")
        if includes_dir.exists():
            for file_path in includes_dir.glob("*.html"):
                if file_path.name == "dropdown.html":
                    continue  # Already processed
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find data.scigem-eng patterns
                    data_patterns = re.findall(
                        r'https://data\.scigem-eng\.sydney\.edu\.au/sand-atlas[^"\'>\s]*',
                        content
                    )
                    
                    for pattern in data_patterns:
                        template_pattern = re.sub(
                            r'\{\{\s*include\.[^}]+\}\}',
                            '{SAND_ID}',
                            pattern
                        )
                        patterns_found.add(template_pattern)
                        
                except Exception as e:
                    print(f"❌ Error reading {file_path}: {e}")
        
        self.results["hosted_data_links"]["patterns"] = list(patterns_found)
        self.results["hosted_data_links"]["sample_urls"] = sample_urls[:5]  # Keep first 5 as examples
        self.results["metadata"]["patterns_checked"] = list(patterns_found)
        
        print(f"✅ Found {len(patterns_found)} unique hosted data patterns")
        return patterns_found
        
    def get_sand_ids(self):
        """Get list of sand IDs from JSON metadata files"""
        sand_ids = []
        json_dir = Path("_data/json")
        
        if json_dir.exists():
            for json_file in json_dir.glob("*.json"):
                sand_id = json_file.stem
                sand_ids.append(sand_id)
                
        print(f"📊 Found {len(sand_ids)} sand types to check")
        return sand_ids
        
    def check_hosted_data_links(self, patterns):
        """Check availability of hosted data files for each sand type"""
        if not HAS_REQUESTS:
            print("⚠️ Skipping hosted data link checking - requests library not available")
            return
            
        sand_ids = self.get_sand_ids()
        
        if not sand_ids:
            print("⚠️ No sand IDs found in _data/json/")
            return
            
        # Limit for quick mode or CI mode
        if self.quick_mode:
            sand_ids = sand_ids[:3]
            print(f"🚀 Quick mode: checking only first {len(sand_ids)} sand types")
        elif self.max_sand_types:
            sand_ids = sand_ids[:self.max_sand_types]
            print(f"🎯 Limited mode: checking first {len(sand_ids)} sand types")
        elif self.ci_mode and len(sand_ids) > 5:
            sand_ids = sand_ids[:5]
            print(f"🤖 CI mode: checking first {len(sand_ids)} sand types to avoid timeouts")
        
        total_checks = 0
        
        for i, sand_id in enumerate(sand_ids, 1):
            print(f"🔍 [{i}/{len(sand_ids)}] Checking hosted data for: {sand_id}")
            
            for pattern in patterns:
                if '{SAND_ID}' in pattern:
                    # Replace the placeholder with actual sand ID
                    url = pattern.replace('{SAND_ID}', f'/{sand_id}/')
                    total_checks += 1
                    
                    try:
                        # Use HEAD request to check availability without downloading
                        response = requests.head(url, timeout=10, allow_redirects=True)
                        
                        link_info = {
                            "url": url,
                            "sand_id": sand_id,
                            "pattern": pattern,
                            "status": response.status_code,
                            "content_type": response.headers.get('content-type', 'unknown')
                        }
                        
                        if response.status_code == 200:
                            self.results["hosted_data_links"]["working"].append(link_info)
                        else:
                            link_info["error"] = f"HTTP {response.status_code}"
                            self.results["hosted_data_links"]["broken"].append(link_info)
                            
                    except requests.exceptions.RequestException as e:
                        self.results["hosted_data_links"]["broken"].append({
                            "url": url,
                            "sand_id": sand_id,
                            "pattern": pattern,
                            "status": None,
                            "error": str(e)
                        })
                    
                    # Be respectful with requests
                    time.sleep(0.3)
                    
            # Progress indicator
            if i % 5 == 0 or i == len(sand_ids):
                working = len(self.results["hosted_data_links"]["working"])
                broken = len(self.results["hosted_data_links"]["broken"])
                print(f"   📈 Progress: {working} working, {broken} broken so far")
        
        print(f"✅ Completed checking {total_checks} hosted data links")
        
    def check_sample_external_links(self):
        """Check a sample of external links from the built site"""
        if not HAS_REQUESTS:
            print("⚠️ Skipping external link checking - requests library not available")
            return
            
        if not self.site_dir.exists():
            print(f"⚠️ Site directory {self.site_dir} not found. Run 'bundle exec jekyll build' first.")
            return
            
        external_links = set()
        
        # Find HTML files in the built site
        for html_file in self.site_dir.rglob("*.html"):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find external links (excluding our hosted data)
                links = re.findall(r'href=["\']([^"\']+)["\']', content)
                for link in links:
                    if (link.startswith(('http://', 'https://')) and 
                        'data.scigem-eng.sydney.edu.au' not in link):
                        external_links.add(link)
                        
                if self.quick_mode and len(external_links) > 10:
                    break  # Limit for quick mode
                    
            except Exception as e:
                print(f"❌ Error reading {html_file}: {e}")
        
        print(f"🌐 Found {len(external_links)} unique external links to check")
        
        # Check a sample of external links
        sample_links = list(external_links)[:10] if self.quick_mode else list(external_links)[:20]
        
        for i, url in enumerate(sample_links, 1):
            print(f"🔗 [{i}/{len(sample_links)}] Checking: {url[:50]}...")
            
            try:
                response = requests.head(url, timeout=15, allow_redirects=True)
                
                link_info = {
                    "url": url,
                    "status": response.status_code
                }
                
                if response.status_code == 200:
                    self.results["external_links"]["working"].append(link_info)
                else:
                    link_info["error"] = f"HTTP {response.status_code}"
                    self.results["external_links"]["broken"].append(link_info)
                    
            except Exception as e:
                self.results["external_links"]["broken"].append({
                    "url": url,
                    "status": None,
                    "error": str(e)
                })
            
            time.sleep(0.2)  # Be respectful
    
    def check_external_links_with_blc(self):
        """Check external links using broken-link-checker (if available)"""
        print("🌐 Checking external links with broken-link-checker...")
        
        try:
            # Check if broken-link-checker is available
            result = subprocess.run(['which', 'blc'], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ broken-link-checker not found, falling back to manual checking")
                return self.check_sample_external_links()
            
            # Run broken-link-checker on the built site
            blc_result = subprocess.run([
                'blc', '--recursive', '--filter-level', '3',
                '--exclude', 'data.scigem-eng.sydney.edu.au',  # Skip hosted data
                '--requests', '10',  # Limit concurrent requests
                '--retry-delay', '1000',  # Add delay between retries
                str(self.site_dir)
            ], capture_output=True, text=True, timeout=300)
            
            # Parse the output
            if blc_result.returncode == 0:
                print("✅ All external links appear to be working")
                # Add some placeholder working links since blc doesn't give detailed output
                self.results["external_links"]["working"].append({
                    "note": "External links checked with broken-link-checker",
                    "status": "passed"
                })
            else:
                print(f"❌ Some external links may be broken")
                # Parse broken links from output
                broken_links = self._parse_blc_output(blc_result.stdout)
                self.results["external_links"]["broken"].extend(broken_links)
                
        except subprocess.TimeoutExpired:
            print("⏰ Link checking timed out, falling back to sample checking")
            return self.check_sample_external_links()
        except Exception as e:
            print(f"❌ Error running broken-link-checker: {e}")
            print("🔄 Falling back to manual checking")
            return self.check_sample_external_links()
    
    def _parse_blc_output(self, output):
        """Parse broken-link-checker output to extract broken links"""
        broken_links = []
        lines = output.split('\n')
        
        for line in lines:
            # Look for lines that indicate broken links
            if '✖' in line or 'BROKEN' in line:
                # Try to extract URL from the line
                url_match = re.search(r'https?://[^\s]+', line)
                if url_match:
                    broken_links.append({
                        "url": url_match.group(0),
                        "error": "Broken link detected by blc",
                        "raw_output": line.strip()
                    })
        
        return broken_links
        
    def check_internal_links(self):
        """Check internal links in the built site"""
        if not self.site_dir.exists():
            print(f"⚠️ Site directory {self.site_dir} not found.")
            return
            
        print("🏠 Checking internal links...")
        internal_links = set()
        
        # Find HTML files and extract internal links
        for html_file in self.site_dir.rglob("*.html"):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find internal links
                links = re.findall(r'href=["\']([^"\']+)["\']', content)
                for link in links:
                    if link.startswith('/') and not link.startswith('//'):
                        internal_links.add(link)
                        
            except Exception as e:
                print(f"❌ Error reading {html_file}: {e}")
        
        print(f"🔍 Found {len(internal_links)} unique internal links to check")
        
        # Check if internal files exist
        for link in list(internal_links)[:20]:  # Limit to avoid too many checks
            # Convert link to file path
            file_path = self.site_dir / link.lstrip('/')
            
            # Try different file extensions
            possible_paths = [
                file_path,
                file_path / "index.html",
                file_path.with_suffix('.html')
            ]
            
            link_exists = any(p.exists() for p in possible_paths)
            
            link_info = {"url": link}
            
            if link_exists:
                self.results["internal_links"]["working"].append(link_info)
            else:
                link_info["error"] = "File not found"
                self.results["internal_links"]["broken"].append(link_info)
                
    def create_github_issue_body(self):
        """Create a GitHub issue body for broken links (CI mode)"""
        if not self.ci_mode:
            return None
            
        broken_hosted = len(self.results["hosted_data_links"]["broken"])
        broken_external = len(self.results["external_links"]["broken"])
        broken_internal = len(self.results["internal_links"]["broken"])
        
        total_broken = broken_hosted + broken_external + broken_internal
        
        if total_broken == 0:
            return None
            
        issue_body = f"""# 🔗 Automated Link Check Report

**Found {total_broken} broken links on {self.results["metadata"]["timestamp"]}**

## 📊 Summary

- 🗂️ Hosted Data Links: {broken_hosted} broken
- 🌐 External Links: {broken_external} broken  
- 🏠 Internal Links: {broken_internal} broken

## 🔧 Action Required

"""

        if broken_hosted > 0:
            issue_body += f"""
### 🗂️ Hosted Data Issues ({broken_hosted})

These files appear to be missing from the data server:

"""
            for link in self.results["hosted_data_links"]["broken"][:10]:  # Limit to first 10
                issue_body += f"- **{link['sand_id']}**: `{link['url']}` - {link['error']}\n"
                
            if len(self.results["hosted_data_links"]["broken"]) > 10:
                issue_body += f"\n*... and {len(self.results['hosted_data_links']['broken']) - 10} more*\n"

        if broken_external > 0:
            issue_body += f"""
### 🌐 External Link Issues ({broken_external})

"""
            for link in self.results["external_links"]["broken"][:5]:
                issue_body += f"- `{link['url'][:80]}...` - {link.get('error', 'Unknown error')}\n"

        if broken_internal > 0:
            issue_body += f"""
### 🏠 Internal Link Issues ({broken_internal})

"""
            for link in self.results["internal_links"]["broken"][:5]:
                issue_body += f"- `{link['url']}` - {link.get('error', 'Unknown error')}\n"

        issue_body += f"""

## 🤖 Automation

This issue was created automatically by the link checker workflow.
- **Workflow**: Link Checker
- **Trigger**: Scheduled check
- **Full Report**: Check the workflow artifacts for detailed results

---
*To disable these notifications, update the `.github/workflows/link-checker.yml` file.*
"""

        return issue_body
    
    def generate_summary(self):
        """Generate summary statistics"""
        hosted_working = len(self.results["hosted_data_links"]["working"])
        hosted_broken = len(self.results["hosted_data_links"]["broken"])
        hosted_total = hosted_working + hosted_broken
        
        external_working = len(self.results["external_links"]["working"])
        external_broken = len(self.results["external_links"]["broken"])
        external_total = external_working + external_broken
        
        internal_working = len(self.results["internal_links"]["working"])
        internal_broken = len(self.results["internal_links"]["broken"])
        internal_total = internal_working + internal_broken
        
        self.results["summary"] = {
            "hosted_data": {
                "total": hosted_total,
                "working": hosted_working,
                "broken": hosted_broken,
                "success_rate": (hosted_working / hosted_total * 100) if hosted_total > 0 else 0
            },
            "external_links": {
                "total": external_total,
                "working": external_working,
                "broken": external_broken,
                "success_rate": (external_working / external_total * 100) if external_total > 0 else 0
            },
            "internal_links": {
                "total": internal_total,
                "working": internal_working,
                "broken": internal_broken,
                "success_rate": (internal_working / internal_total * 100) if internal_total > 0 else 0
            },
            "patterns_found": len(self.results["hosted_data_links"]["patterns"]),
            "total_broken": hosted_broken + external_broken + internal_broken
        }
        
    def generate_report(self, format="markdown"):
        """Generate a report in the specified format"""
        
        if format == "json":
            return json.dumps(self.results, indent=2)
            
        elif format == "markdown":
            return self._generate_markdown_report()
            
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _generate_markdown_report(self):
        """Generate a detailed markdown report"""
        
        summary = self.results["summary"]
        
        report = f"""# 🔗 Sand Atlas Link Check Report

**Generated:** {self.results["metadata"]["timestamp"]}
**Mode:** {"Quick check (sample)" if self.quick_mode else "Full check"}

## 📊 Summary

### Hosted Data Links (data.scigem-eng.sydney.edu.au)
- **Patterns found:** {summary["patterns_found"]}
- **Total links checked:** {summary["hosted_data"]["total"]}
- **✅ Working:** {summary["hosted_data"]["working"]}
- **❌ Broken:** {summary["hosted_data"]["broken"]}
- **Success rate:** {summary["hosted_data"]["success_rate"]:.1f}%

### External Links (Sample)
- **Total links checked:** {summary["external_links"]["total"]}
- **✅ Working:** {summary["external_links"]["working"]}
- **❌ Broken:** {summary["external_links"]["broken"]}
- **Success rate:** {summary["external_links"]["success_rate"]:.1f}%

## 🎯 Hosted Data Patterns Detected

The following URL patterns were automatically detected:

"""
        
        for pattern in self.results["hosted_data_links"]["patterns"]:
            report += f"```\n{pattern}\n```\n\n"
            
        if self.results["hosted_data_links"]["sample_urls"]:
            report += """### Sample Template URLs

"""
            for url in self.results["hosted_data_links"]["sample_urls"]:
                report += f"- `{url}`\n"
                
        if self.results["hosted_data_links"]["broken"]:
            report += f"""
## ❌ Broken Hosted Data Links

"""
            # Group by sand_id for better readability
            broken_by_sand = defaultdict(list)
            for link in self.results["hosted_data_links"]["broken"]:
                broken_by_sand[link['sand_id']].append(link)
                
            for sand_id, links in sorted(broken_by_sand.items()):
                report += f"\n### {sand_id}\n"
                for link in links:
                    file_type = Path(link['url']).suffix or "unknown"
                    report += f"- `{file_type}` - {link['error']}\n"
                    report += f"  - URL: `{link['url']}`\n"
        
        if self.results["external_links"]["broken"]:
            report += f"""
## ❌ Broken External Links

"""
            for link in self.results["external_links"]["broken"]:
                report += f"- `{link['url'][:80]}...` - {link.get('error', 'Unknown error')}\n"
                
        if self.results["hosted_data_links"]["working"]:
            report += f"""
## ✅ Working Hosted Data Links (Sample)

"""
            # Show first few working links as examples
            for link in self.results["hosted_data_links"]["working"][:3]:
                file_type = Path(link['url']).suffix
                report += f"- **{link['sand_id']}** `{file_type}` - {link.get('content_type', 'unknown')}\n"
                
            if len(self.results["hosted_data_links"]["working"]) > 3:
                report += f"\n*... and {len(self.results['hosted_data_links']['working']) - 3} more working links*\n"
        
        future_proofing_text = """
## 🔮 Future Proofing

This link checker is designed to automatically adapt to changes in the Sand Atlas:

1. **🔍 Pattern Detection**: Automatically scans `_includes/dropdown.html` and other templates
2. **📝 Template Awareness**: Understands Jekyll templating (`{{ include.sand }}`)
3. **🏷️ Categorized Results**: Separates hosted data from other external links
4. **📊 Detailed Reporting**: Provides actionable information for fixing broken links

### Adding New Hosted Data Patterns

To support new hosting locations, update the `hosted_data_patterns` list in the script:

```python
self.hosted_data_patterns = [
    r'https://data\\.scigem-eng\\.sydney\\.edu\\.au/sand-atlas/',
    r'https://new-host\\.example\\.com/sand-data/',  # Add new patterns here
    r'{{ include\\.sand }}',
]
```

### Supported File Types

"""
        
        # Add detected file types
        detected_extensions = set()
        for link in self.results['hosted_data_links']['working'] + self.results['hosted_data_links']['broken']:
            suffix = Path(link['url']).suffix
            if suffix:
                detected_extensions.add(suffix)
        
        if detected_extensions:
            future_proofing_text += f"Currently detecting: {', '.join(sorted(detected_extensions))}\n"
        else:
            future_proofing_text += "No file types detected yet.\n"
            
        report += future_proofing_text

        return report
        
    def save_results(self, output_format="both", output_dir="."):
        """Save results to files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        if output_format in ["json", "both"]:
            json_file = output_dir / "link_check_results.json"
            with open(json_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"📄 JSON results saved to: {json_file}")
            
        if output_format in ["markdown", "both"]:
            md_file = output_dir / "link_check_report.md"
            with open(md_file, 'w') as f:
                f.write(self.generate_report("markdown"))
            print(f"📝 Markdown report saved to: {md_file}")
            
    def run(self, hosted_only=False):
        """Run the complete link checking process"""
        print("🚀 Starting Sand Atlas link check...")
        print(f"📁 Site directory: {self.site_dir}")
        print(f"⚡ Mode: {'Quick' if self.quick_mode else 'Full'}")
        print(f"🤖 CI Mode: {self.ci_mode}")
        print(f"🎯 Max sand types: {self.max_sand_types or 'unlimited'}")
        
        # Check dependencies
        if self.ci_mode:
            self._check_ci_dependencies()
        
        # Step 1: Find hosted data patterns
        print("\n🔍 Step 1: Finding hosted data patterns...")
        try:
            patterns = self.find_dropdown_patterns()
        except Exception as e:
            print(f"❌ Error finding patterns: {e}")
            patterns = []
        
        # Step 2: Check hosted data links
        if patterns:
            print("\n📊 Step 2: Checking hosted data availability...")
            try:
                self.check_hosted_data_links(patterns)
            except Exception as e:
                print(f"❌ Error checking hosted data: {e}")
        else:
            print("⚠️ No hosted data patterns found!")
            
        # Step 3: Check external links (unless hosted-only mode)
        if not hosted_only:
            try:
                if self.ci_mode:
                    print("\n🌐 Step 3: Checking external links with broken-link-checker...")
                    self.check_external_links_with_blc()
                else:
                    print("\n🌐 Step 3: Checking sample external links...")
                    self.check_sample_external_links()
            except Exception as e:
                print(f"❌ Error checking external links: {e}")
        
        # Step 4: Check internal links (if in full mode)
        if not self.quick_mode and not hosted_only:
            try:
                print("\n🏠 Step 4: Checking internal links...")
                self.check_internal_links()
            except Exception as e:
                print(f"❌ Error checking internal links: {e}")

        # Step 5: Generate summary and report
        print("\n📋 Step 5: Generating report...")
        try:
            self.generate_summary()
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
        
        print("\n✅ Link check complete!")
        return self.results
        
    def _check_ci_dependencies(self):
        """Check if CI dependencies are available"""
        print("🔧 Checking CI dependencies...")
        
        # Check for requests
        try:
            import requests
            print("   ✅ requests library available")
        except ImportError:
            print("   ❌ requests library not found")
            print("   📦 Install with: pip install requests")
            
        # Check for broken-link-checker
        try:
            import subprocess
            result = subprocess.run(['which', 'blc'], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ broken-link-checker available")
            else:
                print("   ⚠️ broken-link-checker not found")
                print("   📦 Install with: npm install -g broken-link-checker")
        except Exception:
            print("   ⚠️ Could not check for broken-link-checker")


def main():
    """Main function with argument parsing"""
    print("🔗 Sand Atlas Link Checker")
    print("=" * 50)
    
    parser = argparse.ArgumentParser(
        description="Check links in Sand Atlas Jekyll site",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check_links.py                    # Quick check with hosted data
  python check_links.py --full             # Full check including external
  python check_links.py --hosted-only      # Only check hosted data links
  python check_links.py --ci-mode          # CI mode with full checking
  python check_links.py --check-deps       # Check CI dependencies
        """
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Run full check including external and internal links (slower)'
    )
    
    parser.add_argument(
        '--hosted-only',
        action='store_true',
        help='Only check hosted data links (data.scigem-eng.sydney.edu.au)'
    )
    
    parser.add_argument(
        '--ci-mode',
        action='store_true',
        help='Run in CI mode with full checking and external tools'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check if CI dependencies are installed'
    )
    
    parser.add_argument(
        '--site-dir',
        default='_site',
        help='Directory containing compiled Jekyll site (default: _site)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for detailed report (default: print to console)'
    )
    
    args = parser.parse_args()
    
    # Handle dependency check
    if args.check_deps:
        checker = SandAtlasLinkChecker(site_dir=args.site_dir)
        checker._check_ci_dependencies()
        return
    
    # Set up checker with appropriate mode
    quick_mode = not (args.full or args.ci_mode)
    checker = SandAtlasLinkChecker(
        site_dir=args.site_dir,
        ci_mode=args.ci_mode,
        quick_mode=quick_mode
    )
    
    # Run the check
    try:
        results = checker.run(hosted_only=args.hosted_only)
        
        # Generate and display report
        report = checker.generate_report()
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n📄 Detailed report saved to: {args.output}")
        else:
            print("\n" + "=" * 60)
            print("📋 LINK CHECK REPORT")
            print("=" * 60)
            print(report)
            
        # Exit with error code if there are broken links
        summary = results.get("summary", {})
        hosted_broken = summary.get("hosted_data_links", {}).get("broken", 0)
        external_broken = summary.get("external_links", {}).get("broken", 0)
        internal_broken = summary.get("internal_links", {}).get("broken", 0)
        
        total_broken = hosted_broken + external_broken + internal_broken
        
        if total_broken > 0:
            print(f"\n❌ Found {total_broken} broken links")
            exit(1)
        else:
            print("\n✅ All links working!")
            exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Check interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
