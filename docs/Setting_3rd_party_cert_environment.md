# Configuring environment with a third party certificate

## Disclaimer

The purpose of this document is to help a developer during the development and testing 
process where they require a trusted, third party certificate. The process detailed 
below should be used for **TESTING PURPOSES** only and by no means intends to provide 
instructions for configuring an production environment.

## Motivation

Every certificate has to be signed by some CA (Certification Authority). There are many
CAs out there. Some are big, like Google or Amazon, and some are smaller for company-specific environments.
One can also create ones own private CA and use it to sign ones own certificates.
Many Companies choose to create their own CA and issue their own certificates.
The purpose of this document is to provide a walk-through on how to issue your 
own CA-signed certificate and to configure your env to work with your CA and issued certificate.

## General information

- Python comes with a list of trusted CAs. Every certificate signed by those CAs 
will be considered as trusted certificate. Those CAs are located in a file called cacerts.pem. 
  To get the path of this file, run in `python3 -c "import certifi; print(certifi.where())"`  

## Walk-through

### Creating your own CA

In this section we are creating our own CA. We will later use this CA to issue certificate for Conjur.
We will add this CA to the trusted CAs list so that the CLI will trust the certificate
received from Conjur.

1) Create your own folder to store the CA and open a terminal
2) Create a root CA encryption key: `openssl genrsa -des3 -out CA-NAME.key 2048`
3) Create a root CA cert:  `openssl req -x509 -new -nodes -key CA-NAME.key -sha256 -days 1825 -out CA-NAME.pem`
    * Note you will be prompted to provide information about the CA. These values do 
      not effect the integrity of the certificate

### Sign certificate for conjur server

In this section we are issuing our own certificate signed by our new CA to be used by the Conjur server.
Conjur will use this certificate to identify itself to the outside world.
The client, communicating with Conjur, could verify that this certificate was issued by a trusted
source (the CA we created in the previous section) and that Conjur DNS is valid as stated in the 
certificate.

1) Create cert key: `openssl genrsa -out CERT-NAME.key 2048`
    * The CA uses this key to create the certificate. Later on, the CA will need this file to verify the certificate.
2) Generate a CSR (Certificate Signing Request) `openssl req -new -key CERT-NAME.key -out CERT-NAME.csr`
    * Note that you will be prompted for information. The only thing that is important is the common_name section.
    The value for this section should be your Conjur URL.
Create a config file for the signing process. It should resemble the following:
    * ``` 
        authorityKeyIdentifier=keyid,issuer
        basicConstraints=CA:FALSE
        keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
        subjectAltName = @alt_names

        [alt_names]
        DNS.1 = myorg.conjur.com
        DNS.2 = myorg_loadBalancer.conjur.com 
        DNS.3 = ...
      ```  
    * The only thing need to be edited is the [alt_names] section where each DNS should be a possible DNS that 
      could be possessed by your Conjur server (Server-Dns, LB-Dns etc...)

4) Sign your cert: `openssl x509 -req -in CERT-NAME.csr -CA CA-NAME.pem -CAkey CA-NAME.key -CAcreateserial -out CERT-NAME.crt -days 825 -sha256 -extfile [PATH-TO-CONFIG-FILE]`

### Configure the signed cert in Conjur server

In this section we are configuring Conjur server to present the CA-signed upon request.

1) Copy the following files to Conjur server `[CA-NAME.pem,CERT-NAME.crt,CERT-NAME.key]`
2) In Conjur server run the following: 
    * `evoke ca import -f --root CA-NAME.pem`
    * `evoke ca import --key CERT-NAME.key --set CERT-NAME.crt`
    * More on this in 
      [docs](https://docs.cyberark.com/Product-Doc/OnlineHelp/AAM-DAP/Latest/en/Content/Deployment/DAP/dap-deploy-dap.htm)

### Build CLI with your CA included

In this section we add our CA to the CLI's trusted CAs. 
1) Add this CA to the Python trusted CAs
    * Edit the `cacerts.pem` file (see in _General information_ section where to find it) with the 
      content of `CA-NAME.pem` file
2) Build the CLI using Pyinstaller so it will have that CA available to the executable upon verification 
    * `pyinstaller -F ./pkg_bin/conjur`
3) You can also build the CLI using Pyinstaller or for testing the different certificate flows
    * `pyinstaller -F ./pkg_bin/conjur or pyinstaller -F test/util/test_runners/integrations_tests_runner.py`