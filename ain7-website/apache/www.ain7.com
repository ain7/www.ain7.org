<VirtualHost *:80>
    ServerAdmin webmaster@ain7.com
    ServerName www.ain7.com
    ServerAlias ain7.com www.ain7.com ain7.org ain7.enseeiht.fr
    AddDefaultCharset UTF-8
	
    # Redirect all to www.ain7.com
    RewriteEngine On
    RewriteCond %{HTTP_HOST} !=www.ain7.com
    RewriteRule ^(.*)$ http://www.ain7.comorg$1 [L]

    <Location />
        SetHandler python-program
        PythonHandler django.core.handlers.modpython
        SetEnv DJANGO_SETTINGS_MODULE ubuntu_nl.settings
        PythonPath "['/usr/local/django', '/home/dennis/web', '/usr/local/pygments'] + sys.path"
        PythonDebug on
    </Location>

    ErrorLog /var/log/apache2/www.ain7.com_error.log
    LogLevel warn
    CustomLog /var/log/apache2/www.ain7.com_access.log combined
    ServerSignature Off

</VirtualHost>
