<VirtualHost *:80>
    ServerAdmin webmaster@ain7.com
    ServerName forum.ain7.com
    ServerAlias forum.ain7.info forums.ain7.info
        
    DocumentRoot /srv/www/ain7.com/forum/htdocs

    <Directory /srv/www/ain7.com/forum/htdocs>
        Allow from all
        Options FollowSymLinks
        AllowOverride None
    </Directory>

    ErrorLog /var/log/apache2/forum.ain7.com_error.log
    CustomLog /var/log/apache2/forum.ain7.com_access.log combined
    ServerSignature Off

</VirtualHost>

# vim:ft=apache:ts=4:sw=4:et
