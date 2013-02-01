
# PRODUCTION DEPLOYMENT

pip install confine-controller

# MANUAL INSTALLATION
    # IF PRODUCTION
        adduser confine
        su confine
        mkdir ~confine/controller
        cd ~confine/controller
        controller-admin.sh clone communitylab --skeletone communitylab
    
    # IF DEVELOPMENT
        git clone gitosis@git.confine-project.eu:confine/controller.git ~confine/confine-controller
        cd ~confine/confine-controller
        echo ~confine/confine-controller/controller > /usr/local/lib/python2.6/dist-packages/controller.pth
        sudo ln -s ~confine/bin/contine-controller.sh /usr/bin/
    
    # Basic services
    sudo python manage.py install_requirements
    sudo python manage.py setup_postgresql --user confine --password confine --name confine # all porject name by default
    
    # Instance deployment
    python manage.py syncdb
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py collectstatic
    python manage.py loaddata firmware_config
    
    # Full set of stuff (deployment)
    sudo python manage.py create_tinc_server
    sudo python manage.py setup_celeryd
    sudo python manage.py setup_apache2
    sudo python manage.py setup_firmware
    python manage.py update_tincd
    
    # Apply changes
    sudo python manage.py restart_services


# AUTOMATED DEPLOYMENT
    controller-admin.sh full_install --type container --user --db_user


# Move firmware and issues outside of the code base (future?)
# rename fixtures: confine_firmware_config
