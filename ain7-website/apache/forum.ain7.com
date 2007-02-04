<VirtualHost *:80>
	ServerAdmin webmaster@ain7.com
	ServerName forum.ain7.com
    AddDefaultCharset UTF-8
	
	DocumentRoot /srv/www/forum.ain7.com
    
	<Directory />
		Options FollowSymLinks
		AllowOverride None
	</Directory>
    
	<Directory /srv/www/forum.ain7.com>
		Options Indexes FollowSymLinks
		AllowOverride All
		Order allow,deny
		allow from all
	</Directory>

    <Directory /srv/www/forum.ain7.com/cache>
        Order deny,allow
        deny from all
    </Directory>
    <Directory /srv/www/forum.ain7.com/include>
        Order deny,allow
        deny from all
    </Directory>
    <Directory /srv/www/forum.ain7.com/plugins>
        Order deny,allow
        deny from all
    </Directory>
    <Directory /srv/www/forum.ain7.com/temp>
        Order deny,allow
        deny from all
    </Directory>


    RewriteEngine on
    #RewriteBase /
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule forum/(\d+)$ /viewforum.php?id=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule forum/(\d+)/(\d+)$ /viewforum.php?id=$1&p=$2
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule forum/(\d+)/post$ /post.php?fid=$1

    RewriteCond ${REQUEST_URI} !-f
    RewriteRule forum/(\d+)/poll$ /post.php?fid=$1&type=poll
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule message/(\d+)$ /viewtopic.php?pid=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule topic/(\d+)$ /viewtopic.php?id=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule topic/(\d+)/(\d+)$ /viewtopic.php?id=$1&p=$2
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule topic/(\d+)/newposts$ /viewtopic.php?id=$1&action=new
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule topic/(\d+)/lastpost$ /viewtopic.php?id=$1&action=last
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule topic/(\d+)/reply$ /post.php?tid=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule topic/(\d+)/quote/(\d+)$ /post.php?tid=$1&qid=$2
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule ^/?profile/(\d+)$ /profile.php?id=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule ^/?profile/(\d+)/(\w+)$ /profile.php?id=$1&section=$2
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule changeprofile/(\d+)/(\w+)$ /profile.php?id=$1&action=$2
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule search/([a-z][\w_\d]+)$ /search.php?action=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule search/(\d+)$ /search.php?search_id=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule search/(\d+)/(\d+)$ /search.php?search_id=$1&p=$2
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule search/show_user/(\d+)$ /search.php?action=show_user&user_id=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule search$ /search.php
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule delete/(\d+)$ /delete.php?id=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule edit/(\d+)$ /edit.php?id=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule help$ /help.php

    RewriteCond ${REQUEST_URI} !-f
    RewriteRule vote$ /vote.php
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule register$ http://www.ain7.com/accounts/register
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule admin/(\w+)$ /admin_$1.php
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule misc/(\w+)$ /misc.php?action=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule email/(\d+)$ /misc.php?email=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule report/(\d+)$ /misc.php?report=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule unsubscribe/(\d+)$ /misc.php?unsubscribe=$1
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule subscribe/(\d+)$ /misc.php?subscribe=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule login$ /login.php
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule login/forget$ http://www.ubuntu-nl.org/accounts/reset
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule login/(\w+)$ /login.php?action=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule logout/(\d+) /login.php?action=out&id=$1
    
    RewriteCond ${REQUEST_URI} !-f
    RewriteRule userlist$ /userlist.php?%{QUERY_STRING}

    ErrorLog /var/log/apache2/forum.ain7.com_error.log
    LogLevel warn
    CustomLog /var/log/apache2/forum.ain7.com_access.log combined
    ServerSignature Off

</VirtualHost>
