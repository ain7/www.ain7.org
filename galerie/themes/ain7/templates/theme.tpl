{*
 * $Revision: 1 $
 * Read this before changing templates!  http://codex.gallery2.org/Gallery2:Editing_Templates
 *
 * themes/ain7/templates/theme.tpl
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

    {* If Gallery doesn't provide a header, we use the album/photo title (or filename) *}
    {if empty($head.title)}
      <title>{$theme.item.title|markup:strip|default:$theme.item.pathComponent}</title>
    {/if}

    {* Include this theme's style sheet *}
    <link rel="stylesheet" type="text/css" href="{g->theme url="theme.css"}"/>

    <style type="text/css">
	.content {ldelim} width: {$theme.params.contentWidth}px; {rdelim}
	{if !empty($theme.params.thumbnailSize)}
	  {assign var="thumbCellSize" value=$theme.params.thumbnailSize+30}
	  .gallery-thumb {ldelim} width: {$thumbCellSize}px; height: {$thumbCellSize}px; {rdelim}
	  .gallery-album {ldelim} height: {$thumbCellSize+30}px; {rdelim}
	{/if}
    </style>
  </head>


  <body class="gallery">
    <div {g->mainDivAttributes}>
      {*
       * Some module views (eg slideshow) want the full screen.  So for those, we don't draw
       * a header, footer, navbar, etc.  Those views are responsible for drawing everything.
       *}
      {if $theme.useFullScreen}
		{include file="gallery:`$theme.moduleTemplate`" l10Domain=$theme.moduleL10Domain}
      {elseif $theme.pageType == 'progressbar'}
	  {*
	   * Le header du portail de l'AIn7 comprend un header et la barre de navigation
	   *}
		{$ain7_header}
		<div class="content">
	  		{g->theme include="progressbar.tpl"}
		</div>
      {else}
	  {*
	   * Le header du portail de l'AIn7 comprend un header et la barre de navigation
	   *}
    	{$ain7_header}
	    <div class="content">

		<div class="breadcrumb">
		  {g->block type="core.BreadCrumb" skipRoot=true separator="/"}
		</div>

		{* Include the appropriate content type for the page we want to draw. *}
		{if $theme.pageType == 'album'}
		  {g->theme include="album.tpl"}
		{elseif $theme.pageType == 'photo'}
		  {g->theme include="photo.tpl"}
		{elseif $theme.pageType == 'admin'}
		  {g->theme include="admin.tpl"}
		{elseif $theme.pageType == 'module'}
		  {g->theme include="module.tpl"}
		{/if}

<!-- Footer par défaut livré avec Gallery2 >
	<div class="footer">
	  {g->logoButton type="validation"}
	  {g->logoButton type="gallery2"}
	  {g->logoButton type="gallery2-version"}
          {g->logoButton type="donate"}
	</div>
<-->

	    </div> <!-- div content -->

		{$ain7_footer}

      {/if}  {* end of not full screen *}
    </div>

    {*
     * Give Gallery a chance to output any cleanup code, like javascript that needs to be run
     * at the end of the <body> tag.  If you take this out, some code won't work properly.
     *}
    {g->trailer}

    {* Put any debugging output here, if debugging is enabled *}
    {g->debug}
  </body>
</html>
