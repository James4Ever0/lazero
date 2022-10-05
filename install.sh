rm -rf build
rm -rf lazero.egg-info
cd ..
yes | pip3 uninstall lazero
pip3 install ./lazero 
