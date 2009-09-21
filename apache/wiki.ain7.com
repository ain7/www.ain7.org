#
# wiki.ain7.com
#

<VirtualHost *:80>
    ServerAdmin webmaster@ain7.com
    ServerName wiki.ain7.com
    ServerAlias wiki.ain7.porcheron.info
    AddDefaultCharset UTF-8

    <Directory /usr/share/moin/server>
        Order Deny,Allow
        Allow from All
        Satisfy All
        Options +ExecCGI
    </Directory>

    <Directory /srv/www/ain7.com/wiki/htdocs>
        Order Deny,Allow
        Allow from All
        Satisfy All
    </Directory>

    # Use default themes
    Alias           /wiki/ /srv/www/ain7.com/wiki/htdocs/

    AcceptPathInfo  On

    RewriteEngine   On

    RewriteRule     ^/moin(/(.*))?  /$2     [last,R]

    RewriteRule     ^/wiki/         -       [last]
    RewriteRule     ^/robots.txt    -       [last]
    RewriteRule     ^/favicon.ico   -       [last]
    RewriteRule     ^/?(.*)         /usr/share/moin/server/moin.cgi/$1      [last,type=application/x-httpd-cgi]

    ErrorLog /var/log/apache2/wiki.ain7.com_error.log
    LogLevel debug
    CustomLog /var/log/apache2/wiki.ain7.com_access.log combined
    ServerSignature Off

</VirtualHost>

# vim:ft=apache:ts=4:sw=4:et
