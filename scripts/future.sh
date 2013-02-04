confine-controller
    controller
        apps
            common # TODO factor this code into controller/ ?
                management
                    commandas # Create a deploy application ? 
                        setupapache
                        setupceleryd
                        installrequirements # Project_settings_apt_get/pip or introspect installed_apps¿ or split service/app¿
                        setuppostgres
                        restartservices # Project_settings_apt_get/pip 
            users
            permissions
                # TODO templates
            nodes
            slices
            mgmtnetworks
            # Optional applications
            firmware
                management
                    commands
                        setupfirmware
            sfa
            communitynetworks
            api
            groupregistration
            issues
        projects
            baseproject # common stuff ? 
            confine # Confine branding (skeletone)
            communitylab # community-lab branding (our depoloyment)
    scripts
        controller-admin.sh
    docs
    config
        requirements.txt
        apache.conf
        celeryd..
    setup.py

# MANUAL INSTALLATION
# Reference platform: Debian 5.0 Squeeze, Python 2.6 and Django 1.5
    adduser confine
    su confine
    # FOR PRODUCTION
        sudo pip install confine-controller
        controller-admin.sh clone communitylab [ ~confine/controller ] [ --skeletone ]
    # FOR DEVELOPMENT
        git clone gitosis@git.confine-project.eu:confine/controller.git ~confine/confine-controller
        cd ~confine/confine-controller
        sudo echo ~confine/confine-controller/controller > /usr/local/lib/python2.6/dist-packages/controller.pth
        sudo ln -s ~confine/bin/contine-controller.sh /usr/bin/
    # Minimal instance setup
    sudo python manage.py installrequirements [ --minimal ]
    sudo python manage.py setuppostgres [ --user ] [ --password ] [ --name ] [ --noinput ]
    python manage.py syncdb
    python manage.py migrate
    python manage.py createsuperuser
    # Fully featured setup (Optional and not needed for devel)
    sudo python manage.py installrequirements [ --all ]
    sudo python manage.py setupapache
    python manage.py collectstatic
    sudo python manage.py setupceleryd
    sudo python manage.py createtincserver
    python manage.py updatetincd
    sudo python manage.py setupfirmware
    python manage.py loaddata firmwareconfig
    # Apply changes
    sudo python manage.py restartservices


# AUTOMATED DEPLOYMENT
    sudo controller-admin.sh deploy --type ( local, container, bootable, chroot )


# UPDATE STEPS
1. Satisfy your level of requirements
    sudo python manage.py installrequirements [ --all | --minimal ]
2. Update database
    python manage.py syncdb
    python manage.py migrate
3. Apply changes
    sudo python manage.py restartservices


# MIGRATION FROM OLD CODE LAYOUT
1. Remember to save your controller/settings.py file
2. Remove all the code base
3. Install your choice (production or development)
4. Copy your settings.py file into PROJECT_DIR/localsettings.py
5. Remove the line "from .settings_example import *" 
6. GOTO Update steps



# Move firmware and issues outside of the code base (future?)
# rename fixtures: confine_firmware_config



