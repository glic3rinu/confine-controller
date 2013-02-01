
# PRODUCTION DEPLOYMENT

pip install confine-controller
controller-admin.sh install_requeriments

adduser confine
su confine
mkdir ~confine/controller
cd ~confine/controller
controller-admin.sh clone communitylab --skeletone communitylab
# TODO these commands should be runned using python manage.py *****
sudo controller-admin.sh setup_celeryd
sudo controller-admin.sh setup_postgresql --user confine --password confine
sudo controller-admin.sh setup_apache2
sudo controller-admin.sh setup_firmware

python manage.py syncdb
python manage.py migrate
python manage.py createsuperuser

python manage.py collectstatic
python manage.py create_tinc_server
python manage.py loaddata firmware_config
sudo controller-admin.sh restart_services


# DEVELOPMENT #
adduser confine
su confine
git clone gitosis@git.confine-project.eu:confine/controller.git ~confine/confine-controller
cd ~confine/confine-controller
echo ~confine/confine-controller/controller > /usr/local/lib/python2.6/dist-packages/controller.pth
sudo ln -s ~confine/bin/contine-controller.sh /usr/bin/
sudo controller-admin.sh install_requirements --base
sudo controller-admin.sh setup_celeryd
sudo controller-admin.sh setup_postgresql --user confine --password confine

python manage.py syncdb
python manage.py migrate
python manage.py createsuperuser

python manage.py runserver 0.0.0.0:8080



# Virtual server
controller-admin.sh full_install --type container --user --db_user 
