#!/usr/bin/env python3
"""
generate_cloud_report.py
Generates an HTML report summarizing common enterprise cloud adoption drivers,
and creates a pie chart visualizing their relative importance.

Usage:
  1. Create a venv (recommended) and install requirements:
       python -m venv venv
       # On Windows: venv\Scripts\activate
       # On macOS/Linux: source venv/bin/activate
       pip install -r requirements.txt
     requirements.txt contents:
       matplotlib==3.7.2
       pillow==10.1.0

  2. Run:
       python generate_cloud_report.py

  3. Open the generated file:
       cloud_adoption_report.html
"""

from pathlib import Path
import base64
import io
import sys

try:
    import matplotlib.pyplot as plt
except Exception as e:
    print("Error importing matplotlib. Install requirements: pip install matplotlib pillow", file=sys.stderr)
    raise

# ======= Data: drivers and weights (you can edit these) =======
drivers = {
    "Cost Efficiency": 18,
    "Scalability & Elasticity": 16,
    "Speed & Agility": 14,
    "Access to Innovation (AI/ML/DB)": 12,
    "Reliability & Availability": 11,
    "Security & Compliance": 9,
    "Operational Simplicity (Managed Services)": 7,
    "Global Reach/Latency": 6,
    "Business Continuity / DR": 4,
    "Data & Analytics Enablement": 3,
}

driver_explanations = {
    "Cost Efficiency": "Reduce upfront capital expenditure by renting compute & storage; pay-for-use pricing.",
    "Scalability & Elasticity": "Automatically scale resources to meet demand peaks and avoid resource waste.",
    "Speed & Agility": "Provision environments quickly for dev/test/prod, enabling faster releases and experimentation.",
    "Access to Innovation (AI/ML/DB)": "Immediate access to managed AI, databases, analytics and other advanced services.",
    "Reliability & Availability": "Provider SLAs, regional redundancy, and managed networking improve uptime.",
    "Security & Compliance": "Providers offer hardened infrastructure, auditing tools and compliance frameworks; enterprises still retain some responsibility.",
    "Operational Simplicity (Managed Services)": "Offload maintenance (patching, backups, upgrades) so teams focus on product features.",
    "Global Reach/Latency": "Deploy near customers with multiple regions/data centers to reduce latency and serve global users.",
    "Business Continuity / DR": "Easier backup, replication, and multi-region disaster recovery patterns.",
    "Data & Analytics Enablement": "Scalable data stores, data lakes, and managed analytics pipelines accelerate insights.",
}

# ======= Create a pie chart and convert to base64 for embedding =======
def create_pie_image(drivers_dict):
    labels = list(drivers_dict.keys())
    sizes = list(drivers_dict.values())

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,          # labels will be shown in legend to keep pie tidy
        autopct='%1.1f%%',
        startangle=140,
        wedgeprops=dict(linewidth=0.5, edgecolor='white'),
    )
    ax.axis('equal')  # Equal aspect ensures pie is drawn as a circle.
    ax.set_title("Enterprise Cloud Adoption Drivers (relative weights)", fontsize=14)

    # Legend on the right
    ax.legend(wedges, labels, title="Drivers", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    buf = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()
    encoded = base64.b64encode(img_bytes).decode('ascii')
    return encoded

# ======= Build HTML report =======
def build_html(drivers_dict, explanations, pie_b64):
    total = sum(drivers_dict.values())
    rows = []
    for i, (k, v) in enumerate(sorted(drivers_dict.items(), key=lambda kv: -kv[1]), start=1):
        percent = (v / total) * 100
        rows.append(f"""
        <tr>
          <td style="padding:8px; vertical-align:top;">{i}</td>
          <td style="padding:8px; vertical-align:top;"><strong>{k}</strong></td>
          <td style="padding:8px; vertical-align:top;">{v} points</td>
          <td style="padding:8px; vertical-align:top;">{percent:.1f}%</td>
          <td style="padding:8px; vertical-align:top;">{explanations.get(k, '')}</td>
        </tr>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Cloud Adoption Drivers Report</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 24px; color:#111; }}
    header {{ margin-bottom: 20px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    th, td {{ border: 1px solid #ddd; text-align: left; }}
    th {{ background:#f7f7f7; padding:10px; }}
    .card {{ border-radius:8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); padding: 16px; margin-bottom: 18px; }}
    .chart {{ max-width:900px; }}
    footer {{ margin-top:20px; font-size:0.9em; color:#555; }}
  </style>
</head>
<body>
  <header>
    <h1>Cloud Adoption Drivers — Enterprise Analysis</h1>
    <p class="card">This report lists common strategic and technical drivers for enterprise cloud adoption, along with relative weights and brief explanations. You can edit the data values in <code>generate_cloud_report.py</code> to reflect your organization's priorities.</p>
  </header>

  <section class="card">
    <h2>Visual summary</h2>
    <div class="chart">
      <img src="data:image/png;base64,{pie_b64}" alt="pie chart" style="max-width:100%; height:auto; border-radius:6px;">
    </div>
  </section>

  <section class="card">
    <h2>Drivers (ranked)</h2>
    <table>
      <thead>
        <tr><th>#</th><th>Driver</th><th>Weight</th><th>Share</th><th>Short explanation</th></tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </section>

  <section class="card">
    <h2>Short recommendations</h2>
    <ol>
      <li>Map cloud drivers to business KPIs (e.g., time-to-market, TCO, uptime) before migration.</li>
      <li>Prioritize quick wins (dev/test in cloud, backups) while planning security and compliance controls.</li>
      <li>Use managed services for non-core infrastructure to accelerate innovation.</li>
      <li>Run a pilot and measure actual cost/performance before full-scale migration.</li>
      <li>Clarify shared responsibility model and implement guardrails (IAM, logging, encryption).</li>
    </ol>
  </section>

  <footer>
    Generated by <strong>generate_cloud_report.py</strong>. Edit the <code>drivers</code> dict in the script to change weights or add/remove drivers.
  </footer>
</body>
</html>
"""
    return html

def main():
    out_dir = Path.cwd()
    pie_b64 = create_pie_image(drivers)
    html = build_html(drivers, driver_explanations, pie_b64)
    out_file = out_dir / "cloud_adoption_report.html"
    out_file.write_text(html, encoding="utf-8")
    print(f"Report generated: {out_file.resolve()}")
    # optional: open automatically on some platforms
    try:
        import webbrowser
        webbrowser.open(str(out_file.resolve()))
    except Exception:
        pass

if __name__ == "__main__":
    main()
