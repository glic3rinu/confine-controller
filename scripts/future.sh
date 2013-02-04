# TODO settings-> globalsettings localsettings...

Devel
Testing
Production


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




# Move firmware and issues outside of the code base (future?)
# rename fixtures: confine_firmware_config



