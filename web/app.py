from flask import Flask, render_template, request
from scanner.discover import scan_subnet, enrich_all_hosts
from utils.db import save_scan_results

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def dashboard():
    subnet = "192.168.1.0/24"
    hosts = []
    if request.method == "POST":
        subnet = request.form.get("subnet", subnet)
        live_hosts = scan_subnet(subnet)
        hosts = enrich_all_hosts(live_hosts)
        save_scan_results(hosts)
    return render_template("dashboard.html", hosts=hosts, subnet=subnet)

if __name__ == "__main__":
    app.run(debug=True)
