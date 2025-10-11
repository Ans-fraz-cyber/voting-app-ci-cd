import json
import os
from datetime import datetime

def generate_html_report(image_name, json_file, html_file):
    # Read JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Start building HTML
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Trivy Security Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .summary { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #007acc; }
        .vuln-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .vuln-table th { background: #34495e; color: white; padding: 12px; text-align: left; }
        .vuln-table td { padding: 12px; border-bottom: 1px solid #ddd; }
        .critical { background: #ffebee; }
        .high { background: #fff3e0; }
        .medium { background: #fff8e1; }
        .low { background: #e8f5e8; }
        .severity-critical { color: #d32f2f; font-weight: bold; }
        .severity-high { color: #f57c00; font-weight: bold; }
        .severity-medium { color: #fbc02d; font-weight: bold; }
        .severity-low { color: #388e3c; font-weight: bold; }
        .no-vulns { background: #d4edda; color: #155724; padding: 30px; text-align: center; border-radius: 8px; margin: 20px 0; }
        .target-header { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Trivy Security Scan Report</h1>
            <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
"""
    
    # Add summary section
    metadata = data.get('Metadata', {})
    html += f"""
        <div class="summary">
            <h2>📊 Scan Summary</h2>
            <p><strong>🔍 Image Scanned:</strong> {image_name}</p>
            <p><strong>🆔 Image ID:</strong> {metadata.get('ImageID', 'N/A')}</p>
            <p><strong>🔧 Scanner Version:</strong> {metadata.get('Scanner', {}).get('Version', 'N/A')}</p>
        </div>
    """
    
    # Process results
    results = data.get('Results', [])
    total_vulnerabilities = 0
    
    for result in results:
        vulnerabilities = result.get('Vulnerabilities', [])
        total_vulnerabilities += len(vulnerabilities)
        
        html += f"""
        <div class="target-header">
            <h2>🎯 Target: {result.get('Target', 'Unknown')}</h2>
            <p><strong>Type:</strong> {result.get('Type', 'N/A')}</p>
            <p><strong>Vulnerabilities Found:</strong> {len(vulnerabilities)}</p>
        </div>
        """
        
        if vulnerabilities:
            html += """
            <table class="vuln-table">
                <thead>
                    <tr>
                        <th>Vulnerability ID</th>
                        <th>Package</th>
                        <th>Installed Version</th>
                        <th>Severity</th>
                        <th>Fixed Version</th>
                        <th>Title</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for vuln in vulnerabilities:
                severity = vuln.get('Severity', 'UNKNOWN')
                severity_class = severity.lower()
                
                html += f"""
                <tr class="{severity_class}">
                    <td><strong><a href="https://nvd.nist.gov/vuln/detail/{vuln.get('VulnerabilityID', '')}" target="_blank">{vuln.get('VulnerabilityID', 'N/A')}</a></strong></td>
                    <td>{vuln.get('PkgName', 'N/A')}</td>
                    <td>{vuln.get('InstalledVersion', 'N/A')}</td>
                    <td class="severity-{severity_class}">{severity}</td>
                    <td>{vuln.get('FixedVersion', 'Not fixed')}</td>
                    <td>{vuln.get('Title', 'No description')}</td>
                </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
        else:
            html += """
            <div class="no-vulns">
                <h3>✅ No Vulnerabilities Found!</h3>
                <p>This target passed the security scan with no vulnerabilities detected.</p>
            </div>
            """
    
    # Add footer
    html += f"""
        <div style="margin-top: 30px; padding: 20px; background: #ecf0f1; border-radius: 8px; text-align: center;">
            <h3>Report Summary</h3>
            <p><strong>Total Vulnerabilities Across All Targets:</strong> {total_vulnerabilities}</p>
            <p>Generated with ❤️ using Trivy and custom reporting</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(html_file, 'w') as f:
        f.write(html)
    
    print(f"✅ Successfully generated: {html_file}")
    print(f"📊 Total vulnerabilities found: {total_vulnerabilities}")

# Generate reports for all images
images = [
    ("31793179/voting-app-vote:latest", "trivy-reports/vote.html"),
    ("31793179/voting-app-result:latest", "trivy-reports/result.html"),
    ("31793179/voting-app-worker:latest", "trivy-reports/worker.html")
]

# Create directory
os.makedirs("trivy-reports", exist_ok=True)

for image_name, html_file in images:
    json_file = f"temp_{image_name.replace('/', '_').replace(':', '_')}.json"
    
    print(f"🔍 Scanning {image_name}...")
    
    # Generate JSON report
    os.system(f"trivy image --format json -o {json_file} {image_name}")
    
    # Convert to HTML
    if os.path.exists(json_file):
        generate_html_report(image_name, json_file, html_file)
        # Clean up temp JSON file
        os.remove(json_file)
    else:
        print(f"❌ Failed to scan {image_name}")

print("🎉 All Trivy HTML reports generated successfully!")
