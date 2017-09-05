# teetime
# usage for vm
create .config.yml in same dir as script
user1:
    username: <gui number>
    password: <password>
user2:
    username: <gui number>
    password: <password>

#Creating Deployment bundle
cd ~/golf
virtualenv -p /usr/bin/python2.7 env
source env/bin/activate
vi requirements.txt
pip install -r requirements.tx
mkdir src
mkdir native_libs
mkdir dist
mkdir conf
mkdir data
cd ~/golf
cp -rf src conf data dist
cp -rf env/lib/python2.7/site-packages/* dist
cd dist/
zip -r ~/deployment_bundle.zip  .
