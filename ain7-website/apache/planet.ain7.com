<VirtualHost *:80>
    ServerAdmin webmaster@ain7.com
    ServerName planet.ain7.com
    AddDefaultCharset UTF-8
	
    DocumentRoot /srv/www/planet.ain7.com

    <Directory />
        Options FollowSymLinks
	AllowOverride None
    </Directory>

    ErrorLog /var/log/apache2/planet.ain7.com_error.log
    LogLevel warn
    CustomLog /var/log/apache2/planet.ain7.com_access.log combined
    ServerSignature Off

</VirtualHost>
