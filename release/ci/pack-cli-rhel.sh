install_dependencies() {
  sudo yum install python38 -y && \
    sudo yum install binutils -y && \
    sudo pip3 install pyinstaller
}

pack_cli() {
  source venv/bin/activate
  pip3 install -r requirements.txt
  pyinstaller -F ./pkg_bin/conjur
}

main() {
  echo "Installing dependencies..."
  install_dependencies

  echo "Packing executable..."
  pack_cli

  echo "Archiving executable file..."
  cd dist && tar -czvf conjur-cli-darwin.tar.gz conjur

}

main

