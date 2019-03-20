import os

private_key_path = str(os.path.join('data', 'ssl', 'private-key.pem'))
certificate_path = str(os.path.join('data', 'ssl', 'certificate.pem'))
config_path = str(os.path.join('scripts', 'config', 'configuration.cnf'))

generate_private_key_cmd = "openssl genrsa -out " + private_key_path + " 2048"
generate_certificate_cmd = "openssl req -new -x509 -days 365 -key " + private_key_path + " -config " + config_path + \
                           " -out " + certificate_path

os.system(generate_private_key_cmd)
os.system(generate_certificate_cmd)
