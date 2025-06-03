from flask import Flask, render_template
from scanner.discover import scan_subnet, enrich_all_hosts
from utils.db import save_scan_results

app = Flask(__name__)

@app.route("/")
def dashboard():
    subnet = "192.168.1.0/24"
    live_hosts = scan_subnet(subnet)
    enriched_hosts = enrich_all_hosts(live_hosts)
    save_scan_results(enriched_hosts)
    return render_template("dashboard.html", hosts=enriched_hosts)

if __name__ == "__main__":
    app.run(debug=True)