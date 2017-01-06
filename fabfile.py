from fabric.api import env, run, sudo
from fabric.context_managers import cd
from fabric.contrib.files import exists, sed
from fabric.network import ssh

env.user = 'fabric-user'
env.hosts = ['libservdhc7.princeton.edu']
env.repo = 'winthrop-django'
env.gitbase = 'https://www.github.com/Princeton-CDH/'
env.build = 'develop'
env.deploy_prefix = '/var/deploy/'
env.web_prefix = '/var/www/'

env.deploy_dir = '%(deploy_prefix)s%(repo)s/' % env

# Requires the ***local*** location for the SSH key for the fabric user
# You can also load your key into an ssh-agent and bypass this step
# If queried for a password, fabric may actually be asking for the key pass.
# This is a known problem unfortunately.

# TODO: Break up the mile long command strings to something more legible.

# Add a private key file here or load it in your ssh-agent
user_key = None

if user_key is not None:
    env.key_filename = user_key

# Use me to test your SSH and server settings!
def host_type():
    run('uname -s')

def deploy_qa(build=None, rebuild=False):
    '''Runs qa build using env dict
    kwargs:
    build -- git hash or overall branch name ('develop', 'master')
    rebuild -- Boolean, if True removes commit dir and rebuilds
    
    syntax:
    fab deploy_qa:build=<hash>

    '''

    if build is not None:
        env.build = build

    env.deploy_commit_dir = '%(deploy_dir)s%(repo)s-%(build)s' % env
    print(env.deploy_dir)
    print(env.deploy_commit_dir)

    if exists(env.deploy_commit_dir) and rebuild is False:
        # Reset symlinks for apache
        with cd('/var/www/'):
            if exists('%(repo)s' % env):
                sudo('rm -f %(repo)s' % env)
            sudo('ln -s %(deploy_commit_dir)s %(repo)s' % env)

    else:
        if exists(env.deploy_commit_dir):
            sudo('rm -rf %(deploy_commit_dir)s' % env)
        
        with cd(env.deploy_dir):
            sudo('rm -f %(build)s.tar.gz' % env)
            sudo('wget %(gitbase)s%(repo)s/archive/%(build)s.tar.gz' % env)
            sudo('tar xzvf %(build)s.tar.gz' % env)

        with cd(env.deploy_commit_dir):

            # Build venv in env/
            sudo('mkdir env')
            sudo('semanage fcontext -a -t httpd_sys_script_exec_t %(deploy_commit_dir)s/env' % env)
            sudo('restorecon -R -v env/')
            sudo('/var/deploy/build_env.sh')

            # Link local_settings.py for winthrop -- REPO SPECIFIC
            sudo('rm -f winthrop/local_settings.py')
            sudo('ln -s /var/deploy/%(repo)s/local_settings.py winthrop/local_settings.py' % env)


            # Backup mySQL and migrate+collectstatic
            # Uses two scripts deployed server-side per application
            # Avaiable in server scripts repo
            sudo('../make_dump.sh')
            sudo('../migrate_collect.sh')

            # Add wsgi virtualenv setting - REPO SPECIFIC SETTINGS
            with cd('winthrop/'):
                sudo('/var/deploy/prep_wsgi.py %(deploy_commit_dir)s %(deploy_commit_dir)s/env/lib/python3.5/site-packages' % env)

            # Put up a denying robots.txt
            if exists('static/robots.txt'):
                sudo('rm static/robots.txt && ln -s ../../robots.txt static/robots.txt')
            else:
                sudo('ln -s ../../robots.txt static/robots.txt')

            # NOTE: If you install pucas, uncomment these lines to install the templates as part of deploy
            # Copy pucas templates
            # sudo('cp -Rf /var/deploy/django-pucas/pucas/templates/pucas templates/')  
            # sudo('cp templates/pucas/sample-admin-login.html templates/admin/login.html')
        
        # Redo symlinks for apache
        with cd('/var/www/'):
            if exists('%(repo)s' % env):
                sudo('rm -f %(repo)s' % env)
            sudo('ln -s %(deploy_commit_dir)s/  %(repo)s' % env)

        # Set permissions and SELinux
        sudo('chown root:apache -R /var/deploy/ && chmod g+rwx -R /var/deploy')

        # Clean up deploy
        sudo('rm -f %(deploy_dir)s*.tar.gz' % env) 

        # Restart apache
        sudo('systemctl restart httpd24-httpd')


