<?php
/*
 * $Revision: 1 $
 * Read this before changing templates!  http://codex.gallery2.org/Gallery2:Editing_Templates
 *
 * themes/ain7/settings/ain7_header.php
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

define ('AIN7_HEADER_CONST',

'<!--  En-tête du portail AIn7 -->
<div class="header">
    <div class="top_info">
        <!-- Gestion des comptes login/mdp à intégrer pour le forum
        <div class="top_info_right">
            <p>Vous n\'êtes pas authentifié - <a href="/accounts/login/?next=/">Se connecter</a></p>
        </div>
        -->
    </div>

    <div class="logo">
        <h1><a href="' . $ain7_path . '"Portail web AIn7"><span class="dark">AIn7</span>.com</a></h1>
    </div>

</div>


<div class="bar">
    <ul class="ligne1">
        <li><a href="' . $ain7_path . '" accesskey="h">Accueil</a></li>
        <li><a href="' . $ain7_path . 'association/" accesskey="o">L\'association</a></li>
        <li><a href="' . $ain7_path . 'adhesions/" accesskey="o">Adhésions</a></li>
        <li><a href="' . $ain7_path . 'annuaire/" accesskey="a">Annuaire</a></li>
        <li><a href="' . $ain7_path . 'evenements/" accesskey="e">Évènements</a></li>
        <li><a href="' . $ain7_path . 'emploi/" accesskey="s">Service emploi</a></li>
        <li><a href="' . $ain7_path . 'actualites/" accesskey="c">Actualités</a></li>
        <li><a href="' . $ain7_path . 'groupes_regionaux/" accesskey="r">Groupes régionaux</a></li>
        <li><a href="' . $ain7_forum . '" accesskey="f">Forums</a></li>
    </ul>

    <ul class="ligne2">
        <li><a href="' . $ain7_path . 'relations_ecole_etudiants/" accesskey="r">Relations école et étudiants</a></li>
        <li><a href="' . $ain7_path . 'roupes_professionnels/" accesskey="g">Groupes Professionnels</a></li>
        <li><a href="' . $ain7_path . 'media_communication/" accesskey="p">Média & Communication</a></li>
        <li><a href="' . $ain7_path . 'international/" accesskey="i">L\'international</a></li>
        <li><a href="' . $ain7_path . 'voyages/" accesskey="v">Voyages</a></li>
        <li class="active"> <a href="' . $ain7_galerie .'" accesskey="h">Galerie</a></li>
        <li><a href="' . $ain7_path . 'manage/" accesskey="h">Gestion</a></li>
    </ul>
</div> <!-- Fin header portail AIn7 -->');

?>
