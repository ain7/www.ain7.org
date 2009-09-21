<?php
/*
 * $Revision: 1 $
 * Read this before changing templates!  http://codex.gallery2.org/Gallery2:Editing_Templates
 *
 * themes/ain7/settings/ain7_footer.php
 *
 * Gallery - a web based photo album viewer and editor
 *
 * Copyright (C) 2007-2008 AIn7
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 *
 * Design par Laurent Bives inspiré de travaux plus anciens de LanVacation
 * http://www.oswd.org/design/preview/id/2876 et du thème
 * Siriux.net de Nico Kaiser <nico@siriux.net>.
 */

if (!defined('AIN7_CONFIG_LOADED'))
	require 'ain7_config.php';

define ('AIN7_FOOTER_CONST', 

'<!-- Pied de page du htème du portail AIn7 -->
<div class="footer">
	<p> <a href="' . $ain7_path . 'rss/">Flux RSS</a> |
		<a href="' . $ain7_path . 'association/contact/">Contact</a> |
		<a href="' . $ain7_path . 'apropos/">A propos</a> |
		<a href="' . $ain7_path . 'mentions_legales/">Mentions legales</a> |
		<a href="http://jigsaw.w3.org/css-validator/check/referer/">XHTML</a><br />
		&copy; Copyright 2008 AIn7 - Version ' . $ain7_version . '</p>
</div> <!-- fin pied de page portail AIn7 -->');

?>
