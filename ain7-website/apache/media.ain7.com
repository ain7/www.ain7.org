<VirtualHost *:80>
    ServerAdmin webmaster@ain7.com
    ServerName media.ain7.com
    AddDefaultCharset UTF-8
	
    DocumentRoot /srv/www/media.ain7.com

    <Directory />
	Options FollowSymLinks
	AllowOverride None
   </Directory>

   <Directory /var/www/media.ubuntu-nl.org>
       AddType application/x-httpd-cgi .cgi
       Options FollowSymLinks +ExecCGI
       AllowOverride None
       Order allow,deny
       allow from all
    </Directory>

    ErrorLog /var/log/apache2/media.ain7.com_error.log
    LogLevel warn

    CustomLog /var/log/apache2/media.ain7.com_access.log combined
    ServerSignature Off

    RewriteEngine On
    RewriteCond %{REQUEST_FILENAME} -d
    RewriteRule .* /index.cgi

    ErrorDocument 404 /index.cgi
    ErrorDocument 403 /index.cgi
</VirtualHost>
