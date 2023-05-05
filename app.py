import dnslib.server
from dnslib import DNSRecord, DNSHeader, QTYPE, A, CLASS
from flask import Flask, request, render_template

app = Flask(__name__)

# Define the SmartDNS server IP address and port
dns_server_ip = '0.0.0.0'
dns_server_port = 53

# Define the default IP address to resolve the domain to
default_resolved_ip = '192.168.1.100'

# Read the DNS records from a file and store them in a dictionary
dns_records = {}
with open('dns_records.txt', 'r') as f:
    for line in f:
        domain, ip_address = line.strip().split()
        dns_records[domain] = A(ip_address)

# Define the handler function to serve DNS queries
def handle_dns_request(request, address, socket):
    # Check if the request is for one of the domains in dns_records
    domain = str(request.q.qname)[:-1]
    if domain in dns_records:
        # Send the DNS record for the domain back to the client
        dns_record = DNSRecord(
            DNSHeader(),
            q=DNSRecord.question(domain, QTYPE.A),
            a=dns_records[domain],
        )
        socket.sendto(dns_record.pack(), address)
    else:
        # Forward the DNS request to another DNS server
        dns_response = dnslib.DNSResolver().request(request, '8.8.8.8')
        socket.sendto(dns_response.pack(), address)

# Define a Flask route to display the form for updating DNS records
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', dns_records=dns_records)

# Define a Flask route to update DNS records
@app.route('/', methods=['POST'])
def update_dns_records():
    # Update the DNS records with the values from the form
    for domain, ip_address in request.form.items():
        if ip_address.strip() == '':
            ip_address = default_resolved_ip
        dns_records[domain] = A(ip_address)
    # Write the updated DNS records to the file
    with open('dns_records.txt', 'w') as f:
        for domain, ip_address in dns_records.items():
            f.write('{} {}\n'.format(domain, ip_address))
    return render_template('index.html', dns_records=dns_records, 
success=True)

# Create a DNSServer instance and start serving requests
server = dnslib.server.DNSServer(
    handle_dns_request,
    address=dns_server_ip,
    port=dns_server_port,
)
server.start()

# Start the Flask app
if __name__ == '__main__':
    app.run()

