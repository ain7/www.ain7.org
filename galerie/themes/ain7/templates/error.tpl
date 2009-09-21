{*
 * $Revision: 1 $
 * Read this before changing templates!  http://codex.gallery2.org/Gallery2:Editing_Templates
 *
 * themes/ain7/templates/error.tpl
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
 *}
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="{g->language}" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    {* Let Gallery print out anything it wants to put into the <head> element *}
    {g->head}

    {* If Gallery doesn't provide a header, insert our own. *}
    {if empty($head.title)}
      <title>{g->text text="Error!"}</title>
    {/if}

    {* Include this theme's style sheet *}
    <link rel="stylesheet" type="text/css" href="{g->theme url="theme.css"}"/>
  </head>
  <body class="gallery">
    <div {g->mainDivAttributes}>
      {include file=$theme.errorTemplate}
    </div>

    {* Put any debugging output here, if debugging is enabled *}
    {g->debug}
  </body>
</html>
