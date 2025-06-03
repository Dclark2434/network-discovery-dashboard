from flask import Flask, render_template, request
from scanner.discover import scan_subnet, enrich_all_hosts
from utils.db import save_scan_results, get_latest_scan_results
from utils.helpers import sanitize_subnet

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def dashboard():
    subnet = "192.168.1.0/24"
    hosts = get_latest_scan_results()
    if request.method == "POST":
        raw_subnet = request.form.get("subnet", subnet)
        try:
            subnet = sanitize_subnet(raw_subnet)
            live_hosts = scan_subnet(subnet)
            hosts = enrich_all_hosts(live_hosts)
            save_scan_results(hosts)
        except ValueError:
            # Invalid input - ignore to avoid injection or crashes
            pass
    return render_template("dashboard.html", hosts=hosts, subnet=subnet)

if __name__ == "__main__":
    app.run(debug=True)
