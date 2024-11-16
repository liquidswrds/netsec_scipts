#!/bin/bash

# Check if BIND9 is installed, install if necessary
if ! command -v named &> /dev/null; then
    echo "Installing BIND9..."
    sudo apt update
    sudo apt install bind9 bind9utils bind9-doc -y
else
    echo "BIND9 is already installed. Skipping installation."
fi

# Variables
ZONE_NAME="csec2324.edu"
ZONE_FILE="/etc/bind/zones/db.${ZONE_NAME}"
NAMED_CONF="/etc/bind/named.conf.local"

# Get the IP address of the ens4 interface
INTERFACE="ens4"
IP_ADDRESS=$(ip -4 addr show ${INTERFACE} | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
if [ -z "$IP_ADDRESS" ]; then
    echo "Error: Could not retrieve IP address for interface ${INTERFACE}. Exiting."
    exit 1
fi

# Create the zones directory if it doesn't exist
if [ ! -d "/etc/bind/zones" ]; then
    mkdir -p /etc/bind/zones
fi

# Add zone entry to named.conf.local if not present
if ! grep -q "${ZONE_NAME}" "${NAMED_CONF}"; then
    echo "Adding zone to ${NAMED_CONF}..."
    echo "
zone \"${ZONE_NAME}\" {
    type master;
    file \"${ZONE_FILE}\";
    allow-transfer { any; };  # Allow all transfers
};" >> ${NAMED_CONF}
else
    echo "Zone already configured in ${NAMED_CONF}"
fi

# Create the zone file with DNS records (abbreviated for brevity)
echo "Creating zone file ${ZONE_FILE}..."

# List of Star Wars character names to use as hostnames
STAR_WARS_NAMES=(
    "luke" "leia" "han" "chewbacca" "yoda" "vader" "anakin" "padme" "obiwan" "qui-gon"
    "jabba" "boba" "jango" "palpatine" "windu" "grievous" "ahsoka" "kylo" "finn" "rey"
    "lando" "tarkin" "phasma" "snoke" "bb8" "r2d2" "c3po" "maul" "dooku" "jarjar"
)

# Create the zone file with SOA and NS records
echo "Creating zone file ${ZONE_FILE}..."

cat <<EOT > ${ZONE_FILE}
\$TTL 604800
@       IN      SOA     ns1.${ZONE_NAME}. admin.${ZONE_NAME}. (
                          2         ; Serial
                     604800         ; Refresh
                      86400         ; Retry
                    2419200         ; Expire
                     604800 )       ; Negative Cache TTL
; Name servers
@       IN      NS      ns1.${ZONE_NAME}.
ns1     IN      A       ${IP_ADDRESS}

; Mail servers
@       IN      MX      10 mail1.${ZONE_NAME}.
@       IN      MX      20 mail2.${ZONE_NAME}.
@       IN      MX      30 mail3.${ZONE_NAME}.
mail1   IN      A       ${IP_ADDRESS}
mail2   IN      A       ${IP_ADDRESS}
mail3   IN      A       ${IP_ADDRESS}

; Web servers
www     IN      A       ${IP_ADDRESS}

; FTP server
ftp     IN      A       ${IP_ADDRESS}

; Additional A records for hosts
EOT

# Generate A records for 30 unique hostnames, skipping IPs .1 to .6
for i in $(seq 7 36); do
    echo "${STAR_WARS_NAMES[$((i-7))]}   IN      A       10.1.1.$i" >> ${ZONE_FILE}
done

# Add CNAME, TXT, SRV, PTR, and other records
cat <<EOT >> ${ZONE_FILE}
; CNAME records
db      IN      CNAME   web1

; TXT records
@       IN      TXT     "v=spf1 include:spf.${ZONE_NAME} -all"
info    IN      TXT     "This is a sample TXT record"

; SRV records
_ldap._tcp      IN      SRV     0 5 389 ldap.${ZONE_NAME}.
_sip._udp       IN      SRV     0 5 5060 sip.${ZONE_NAME}.

; PTR records (if reverse DNS was needed - shown here for example)
${IP_ADDRESS}.in-addr.arpa.   IN      PTR     www.${ZONE_NAME}.

; Other records
localhost IN      A       127.0.0.1
EOT

# Set permissions for the zone file
chown root:bind ${ZONE_FILE}
chmod 644 ${ZONE_FILE}

# Restart BIND service
echo "Restarting BIND9 service..."
systemctl restart bind9
echo "BIND9 DNS setup complete. Various DNS records have been added with IP ${IP_ADDRESS}."

# Check if Apache2 is installed, install if necessary
if ! command -v apache2 &> /dev/null; then
    echo "Installing Apache2..."
    sudo apt install apache2 -y
else
    echo "Apache2 is already installed. Skipping installation."
fi

# Create a virtual host file
sudo tee /etc/apache2/sites-available/${ZONE_NAME}.conf > /dev/null <<EOF
<VirtualHost *:80>
    ServerName www.${ZONE_NAME}
    ServerAlias ${ZONE_NAME}
    DocumentRoot /var/www/${ZONE_NAME}

    <Directory /var/www/${ZONE_NAME}>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog \${APACHE_LOG_DIR}/${ZONE_NAME}_error.log
    CustomLog \${APACHE_LOG_DIR}/${ZONE_NAME}_access.log combined
</VirtualHost>
EOF

# Create the Star Wars themed website directory and index page
sudo mkdir -p /var/www/${ZONE_NAME}
sudo tee /var/www/${ZONE_NAME}/index.html > /dev/null <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to the Galaxy</title>
    <style>
        body {
            background-color: black;
            color: yellow;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
        }
        h1 {
            font-size: 3em;
            margin: 0.5em 0;
        }
        .intro {
            font-size: 1.2em;
            max-width: 600px;
            margin: 0 auto;
            padding: 1em;
            background: rgba(255, 255, 0, 0.1);
            border-radius: 8px;
        }
        .character {
            margin: 1.5em 0;
            padding: 1em;
            font-size: 1.5em;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: lightgray;
        }
        .footer {
            font-size: 0.8em;
            color: gray;
            margin-top: 2em;
        }
    </style>
</head>
<body>
    <h1>Welcome to the Galaxy of ${ZONE_NAME}</h1>
    <div class="intro">
        <p>"A long time ago in a galaxy far, far away..."</p>
        <p>Welcome to the Star Wars-themed world of ${ZONE_NAME}. May the Force be with you as you explore!</p>
    </div>
    <div class="character">
        <h2>Yoda</h2>
        <p>"Do, or do not. There is no try."</p>
    </div>
    <div class="character">
        <h2>Darth Vader</h2>
        <p>"I find your lack of faith disturbing."</p>
    </div>
    <div class="character">
        <h2>Leia Organa</h2>
        <p>"Help me, Obi-Wan Kenobi. You're my only hope."</p>
    </div>
    <div class="footer">
        <p>Star Wars and all related characters and elements are © & ™ Lucasfilm Ltd.</p>
        <p>This is a fan site for educational purposes only.</p>
    </div>
</body>
</html>
EOF

# Enable the new site and reload Apache
sudo a2ensite ${ZONE_NAME}.conf
sudo systemctl reload apache2
echo "Star Wars-themed website setup complete. Visit http://www.${ZONE_NAME} to explore the galaxy!"

