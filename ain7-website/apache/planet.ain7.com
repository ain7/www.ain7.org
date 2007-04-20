#
# planet.ain7.com
#

<VirtualHost *:80>
    ServerAdmin webmaster@ain7.com
    ServerName planet.ain7.com
    AddDefaultCharset UTF-8
	
    DocumentRoot /srv/www/ain7.com/planet/htdocs

    <Directory /srv/www/ain7.com/planet/htdocs>
        Allow from all
        Options FollowSymLinks
        AllowOverride None
    </Directory>

    ErrorLog /var/log/apache2/planet.ain7.com_error.log
    LogLevel warn
    CustomLog /var/log/apache2/planet.ain7.com_access.log combined
    ServerSignature Off

</VirtualHost>

# vim:ft=apache:ts=4:sw=4:et
