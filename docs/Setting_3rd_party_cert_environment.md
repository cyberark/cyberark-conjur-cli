# Set 3rd party cert environment

##Disclaimer
This doc intention is to help developer with building environment using 3rd party certificate,
Used for **TESTING PURPOSE** and by no means provide an instruction on how to set up a production environment

## Motivation

Every certificate has to be signed by some CA (Certification Authority). There are many
CA's out there. Some are big, like Google or Amazon, and some are small CA's.
One can also create it own private CA and signed it own certificates.
Many Companies (mostly big companies) choose to create their own CA and issue 
their own certificates. This doc purpose is to be a walk-through on how to issue 
your own certificate and to configure your env to work with your CA and issued certificate.

## General information
- Python comes with a list of trusted CAs. Every certificate signed by those CAs 
will be considered as trusted certificate. Those CAs are located in a file called cacerts.pem. 
  To get the path of this file, run in python `import certifi; certifi.where()` 

## Walk-through
### Creating your own CA
1) Create your own folder to store the CA and open a terminal
2) Create a rootCA encryption key: `openssl genrsa -des3 -out CA-NAME.key 2048`
3) Create a rootCA cert:  `openssl req -x509 -new -nodes -key CA-NAME.key -sha256 -days 1825 -out CA-NAME.pem`
    * Note you will be asked to prompt some information about the CA this values are not affecting 
      the process by any way

### Sign certificate for conjur server
1) Create cert key: `openssl genrsa -out CERT-NAME.key 2048`
2) Generate csr (certificate signing request) : `openssl req -new -key CERT-NAME.key -out CERT-NAME.csr`
    * Note that you will need to provide information. the only thing that is important is the Common_name section.
    The value for this section should be your conjur url.
3) create a config file for the signing process. should look like this
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
      * The only thing need to be edited is the [alt_names] section where each dns should be a possible dns that 
        could be possessed by your conjur server
4) Sign your cert: `openssl x509 -req -in CERT-NAME.csr -CA CA-NAME.pem -CAkey CA-NAME.key -CAcreateserial -out CERT-NAME.crt -days 825 -sha256 -extfile [PATH-TO-CONFIG-FILE]`

### apply cert in conjur server
1) Copy the followings to conjur server `[CA-NAME.pem,CERT-NAME.crt,CERT-NAME.key]`
2) In conjur server run the following: 
    * `evoke ca import -f --root CA-NAME.pem`
    * `evoke ca import --key CERT-NAME.key --set CERT-NAME.crt`
    * More on this in [docs](https://docs.cyberark.com/Product-Doc/OnlineHelp/AAM-DAP/Latest/en/Content/Deployment/DAP/dap-deploy-dap.htm)
### Build CLI with your CA included
1) Add this CA to the python trusted CAs
    * edit the `cacerts.pem` file (see in _General information_ section where to find it) the 
      content of `CA-NAME.pem` file
2) build the CLI using pyinstaller 
    * `pyinstaller -F ./pkg_bin/conjur`