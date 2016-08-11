/* To avoid CSS expressions while still supporting IE 7 and IE 6, use this script */
/* The script tag referencing this file must be placed before the ending body tag. */

/* Use conditional comments in order to target IE 7 and older:
	<!--[if lt IE 8]><!-->
	<script src="ie7/ie7.js"></script>
	<!--<![endif]-->
*/

(function() {
	function addIcon(el, entity) {
		var html = el.innerHTML;
		el.innerHTML = '<span style="font-family: \'icomoon\'">' + entity + '</span>' + html;
	}
	var icons = {
		'icon-accounting5': '&#xe900;',
		'icon-book200': '&#xe901;',
		'icon-book236': '&#xe902;',
		'icon-caduceus8': '&#xe903;',
		'icon-chemistry29': '&#xe904;',
		'icon-cocktail32': '&#xe905;',
		'icon-earth132': '&#xe906;',
		'icon-educational18': '&#xe907;',
		'icon-group2': '&#xe908;',
		'icon-statistics': '&#xe909;',
		'icon-teacher4': '&#xe90a;',
		'icon-user255': '&#xe90b;',
		'icon-win5': '&#xe90c;',
		'0': 0
		},
		els = document.getElementsByTagName('*'),
		i, c, el;
	for (i = 0; ; i += 1) {
		el = els[i];
		if(!el) {
			break;
		}
		c = el.className;
		c = c.match(/icon-[^\s'"]+/);
		if (c && icons[c[0]]) {
			addIcon(el, icons[c[0]]);
		}
	}
}());
