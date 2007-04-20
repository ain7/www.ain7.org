#
# www.ain7.com
#

<VirtualHost *:80>
    ServerAdmin webmaster@ain7.com
    ServerName www.ain7.com
    ServerAlias ain7.com www.ain7.com ain7.org ain7.enseeiht.fr
    AddDefaultCharset UTF-8

    # Redirect all to www.ain7.com
    #RewriteEngine On
    #RewriteCond %{HTTP_HOST} !=www.ain7.com
    #RewriteRule ^(.*)$ http://www.ain7.com$1 [L]

    DocumentRoot /srv/www/ain7.com/www/htdocs

    <Location />
        SetHandler python-program
        PythonHandler django.core.handlers.modpython
        SetEnv DJANGO_SETTINGS_MODULE ain7.settings
        PythonPath "['/srv/www/ain7.com/www/'] + sys.path"
        PythonDebug on
    </Location>

    <Directory /srv/www/ain7.com/www/htdocs>
        Allow from all
        Options FollowSymLinks
        AllowOverride None
    </Directory>

    ErrorLog /var/log/apache2/www.ain7.com_error.log
    LogLevel warn
    CustomLog /var/log/apache2/www.ain7.com_access.log combined
    ServerSignature Off

</VirtualHost>

# vim:ft=apache:ts=4:sw=4:et
