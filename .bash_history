ls
nano Dockerfile7
ls
rm Dockerfile7
ls
sudo apt-get update
sudo apt-get install     apt-transport-https     ca-certificates     curl     gnupg-agent     software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
apt-cache madison docker-ce
sudo apt-get install docker-ce=5:19.03.7~3-0~ubuntu-bionic docker-ce-cli=5:19.03.7~3-0~ubuntu-bionic containerd.io
sudo docker run hello-world
sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
ls
mkdir RIDES
mv rides.py RIDES
ls
mv Dockerfile RIDES
ls
cd RIDES
ls
nano docker-compose.yml
ls
cd ..
nano docker-compose.yml
ls
nano docker-compose.yml
cs RIDES
ls RIDES
nano Dockerfile
cd RIDES

nano Dockerfile
cd ..
sudo docker-compose up
ls
sudo docker ps
sudo docker-compose down
sudo docker ps
ls
cd RIDES
ls
nano rides.py
nano Dockerfile
cd ..
sudo docker-compose up
sudo docker-compose down
ls
cd RIDES
nano rides.py
cd ..
sudo docker-compose up
ls
cd RIDES
nano rides.py
sudo docker-compose down
docker image build -t rides .
sudo docker image build -t rides .
cd ..
sudo docker-compose up
