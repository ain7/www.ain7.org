var FloatingPane = new Class({

	// default args
	width: 400,
	height: 200,
	draggable: false,
	opacity: 0.5,
	zIndex: 200,
	title: "",

	initialize: function(args) {
		if(args) {
			this.width = args.width || this.width;
			this.height = args.height || this.height;
			this.draggable = args.draggable || this.draggable;
			this.opacity = args.opacity || this.opacity;
			this.zIndex = args.zIndex || this.zIndex;
			this.title = args.title || this.title;
		}
	
		this.container = new Element('div', {
			'class': 'floatingPaneContainer',
			'styles': {
				'display': 'none',
				'position': 'absolute',
				'zIndex': this.zIndex + 1,
				'backgroundColor': 'white',
				'width': this.width
			}
		}).inject(document.body);

		this.filter = new Element('div', {
			'styles': {
				'position': 'absolute',
			 	'display': 'none',
			 	'zIndex': this.zIndex,
			 	'backgroundColor': "black"
			}
		}).setOpacity(this.opacity).inject(document.body);
		
		
		// Header
		var header = new Element('div', {
			'class': 'hd',
			'styles': {
				'overflow': 'hidden'
			}
		}).inject(this.container);
		
		// make this floating pane draggable if the property is set
		if(this.draggable) {
			new Drag.Base(this.container, {handler: header});
			header.style.cursor = 'move';
		}
		
		this.titleContainer = new Element('span').setText(this.title).inject(header);
		
		var closeImage = new Element('div', {
			'class': 'close',
			'styles': {
				'cursor': 'pointer'
			},
			'events': {
				'mouseover': function() {
					this.className = 'close-over';
				},
				'mouseout': function() {
					this.className = 'close';
				},
				'click': function(e) {
					this.close(e);
				}.bindWithEvent(this)
			}
		}).inject(header);
		
		// Body
		var body = new Element('div', {
			'class': 'bd',
			'styles': {
				'height': this.height
			}
		}).inject(this.container);
		
		this.pleasewait = new Element('div', {
			'class': 'pleaseWait'
		}).inject(body);
		
		this.content = new Element('iframe', {
			'styles': {
				'width': this.width,
				'height': 0
			}
		}).inject(body);
		
		// firefox specific
		this.content.onload = function() {
			this.onContentready();
		}.bind(this);
		
		// IE specific
		this.content.onreadystatechange = function() {
			if(this.content.readyState == "complete") {
				this.onContentready();
			}
		}.bind(this);

		window.addEvent("resize", function() {
			this.center();
		}.bind(this));
	},

	onContentready: function() {
		this.pleasewait.style.display = "none";
		this.content.style.height = this.height + "px";
	},

	show: function(contentUrl, title) {
		this.container.style.display = "block";
		this.filter.style.display = "block";
		this.pleasewait.style.display = "block";
		this.content.style.height = "0px";
		this.titleContainer.setText(title || this.title);
		this.content.src = contentUrl;
		this.center();
	},

	close: function(e) {
		this.container.style.display = "none";
		this.filter.style.display = "none";
		this.fireEvent('onFloatingPaneClose', e);
	},

	center: function() {
		var coordinates = this.container.getCoordinates();
		this.container.setStyles({
				top: window.getHeight()/2 - coordinates.height/2,
				left: window.getWidth()/2 - coordinates.width/2
		});
		this.filter.setStyles({
			height: window.getHeight(),
				width: window.getWidth(),
				top: 0,
				left: 0
		});
	}
});

FloatingPane.implement(new Events);
