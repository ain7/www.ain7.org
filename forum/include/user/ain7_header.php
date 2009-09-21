<?php
if (!defined('AIN7_CONFIG_LOADED'))
	require 'ain7_config.php';
?>


<!--  En-tête du portail AIn7 -->
<div class="header">
    <div class="top_info">
        <!-- Gestion des comptes login/mdp à intégrer pour le forum
        <div class="top_info_right">
            <p>Vous n'êtes pas authentifié - <a href="/accounts/login/?next=/">Se connecter</a></p>
        </div>
        -->
    </div>

    <div class="logo">
        <h1><a href="<?php echo $ain7_path; ?>"Portail web AIn7"><span class="dark">AIn7</span>.com</a></h1>
    </div>

</div>


<div class="bar">
    <ul class="ligne1">
        <li><a href="<?php echo $ain7_path; ?>" accesskey="h">Accueil</a></li>
        <li><a href="<?php echo $ain7_path; ?>association/" accesskey="o">L'association</a></li>
        <li><a href="<?php echo $ain7_path; ?>adhesions/" accesskey="o">Adhésions</a></li>
        <li><a href="<?php echo $ain7_path; ?>annuaire/" accesskey="a">Annuaire</a></li>
        <li><a href="<?php echo $ain7_path; ?>evenements/" accesskey="e">Évènements</a></li>
        <li><a href="<?php echo $ain7_path; ?>emploi/" accesskey="s">Service emploi</a></li>
        <li><a href="<?php echo $ain7_path; ?>actualites/" accesskey="c">Actualités</a></li>
        <li><a href="<?php echo $ain7_path; ?>groupes_regionaux/" accesskey="r">Groupes régionaux</a></li>
        <li class="active"><a href="<?php echo $ain7_forum; ?>" accesskey="f">Forums</a></li>
    </ul>

    <ul class="ligne2">
        <li><a href="<?php echo $ain7_path; ?>relations_ecole_etudiants/" accesskey="r">Relations école et étudiants</a></li>
        <li><a href="<?php echo $ain7_path; ?>groupes_professionnels/" accesskey="g">Groupes Professionnels</a></li>
        <li><a href="<?php echo $ain7_path; ?>media_communication/" accesskey="p">Média & Communication</a></li>
        <li><a href="<?php echo $ain7_path; ?>international/" accesskey="i">L'international</a></li>
        <li><a href="<?php echo $ain7_path; ?>voyages/" accesskey="v">Voyages</a></li>
        <li><a href="<?php echo $ain7_galerie; ?>" accesskey="h">Galerie</a></li>
        <li><a href="<?php echo $ain7_path; ?>manage/" accesskey="h">Gestion</a></li>
    </ul>
</div> <!-- Fin header portail AIn7 -->


