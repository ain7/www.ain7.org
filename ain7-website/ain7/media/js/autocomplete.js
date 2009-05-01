var AutoComplete = new Class({

	Extends: Request,
	
	isFrozen: false,
	currentSelection: -1,

	options: {
		resultListHeight: 200,
		zIndex: 1
	},

	initialize: function(input, url, displayValue, options, hideninput) {
		this.input = $(input);
		this.hideninput = $(hideninput);
		this.displayValue = displayValue;
		this.setOptions(options);
		this.parent(url);

		width = this.input.getStyle('width');
		if (parseInt(width) < 0)
		{
			// IE may return a negative width.
			width = "250px";
		}
		// the div to display the results
		this.resultContainer = new Element('div', {
			'id': hideninput.id + 'autocompleteResultContainer',
			'class': 'autocompleteResultContainer',
			'styles': {
				'display': 'none',
				'position': 'absolute',
				'zIndex': this.options.zIndex,
				'width': width,
				'height': this.options.resultListHeight
			}
		}).inject(document.body,'top');
		this.setResultContainerPosition();
		this.options.update = this.resultContainer;

		// connect the input field keyup event to this Ajax requester
		this.input.addEvent('keyup', function(e) {
			if(!this.isFrozen) {
				switch(e.code) {
					case Event.Keys.up:
					case Event.Keys.down:
					case Event.Keys.left:
					case Event.Keys.right:
					case Event.Keys.tab:
					case Event.Keys.enter:
					break;
					case Event.Keys.esc:
						this.resultContainer.style.display = "none";
						break;
					default: {
						var data = {};
						data[this.input.name] = this.input.value;
						this.send({url: url, data: data});
						this.hideninput.value = "-1";
					}
				}
			}
		}.bind(this));

		this.input.addEvent('keydown', function(e) {
			if(e.code == Event.Keys.tab) {
				this.resultContainer.style.display = "none";
			}
		}.bind(this));


		this.addEvent('onComplete', this._onResultReceived);

		// close the result list when click elsewhere
		document.addEvent("click", function(e) {
			if(!this.isFrozen) {
				if(e.target != this.input) {
					this.resultContainer.style.display = "none";
				}
			}
		}.bindWithEvent(this));

		// navigate in the result list with the up & down arrow
		document.addEvent('keyup', function(e) {
			if(!this.isFrozen) {
				switch(e.code) {
					case Event.Keys.up:
						this._navigateOnResult(true);
					break;
					case Event.Keys.down:
						this._navigateOnResult(false);
					break;
					case Event.Keys.enter:
						if(this.resultContainer.style.display == "block" && this.currentSelection >= 0) {
							this._onItemSelect(this.resultList[this.currentSelection]);
						}
				}
			}
		}.bind(this));

		window.addEvent("resize", function() {
			this.setResultContainerPosition();
		}.bind(this));
	},

	_navigateOnResult: function(/*boolean*/ up) {
		if(this.resultList && this.resultList.length > 0) {
			this.input.blur();
			if(up) {
				if(this.currentSelection > 0) {
					this.resultList[this.currentSelection].removeClass("selected");
					var item = this.resultList[this.currentSelection - 1];
					item.addClass("selected");
					if(item.offsetTop < this.resultContainer.scrollTop) {
						var itemHeight = item.offsetHeight + item.getStyle('margin-top').toInt() + item.getStyle('margin-bottom').toInt();
						this.resultContainer.scrollTop -= itemHeight;
					}
					this.currentSelection--;
				}
			} else {
				if(this.currentSelection < this.resultList.length - 1) {
					if(this.currentSelection >= 0) {
						 this.resultList[this.currentSelection].removeClass("selected");
					}
					var item = this.resultList[this.currentSelection + 1];
					item.addClass("selected");
					var itemHeight = item.offsetHeight + item.getStyle('margin-top').toInt() + item.getStyle('margin-bottom').toInt();
					if(item.offsetTop + itemHeight > this.resultContainer.scrollTop + this.options.resultListHeight) {
						this.resultContainer.scrollTop += itemHeight;
					}
					this.currentSelection++;
				}
			}
		}
	},

	setResultContainerPosition: function() {
		var inputCoords = this.input.getCoordinates();
		this.resultContainer.setStyles({
			top: inputCoords.bottom,
			left: inputCoords.left
		});
	},

	_onResultReceived: function(result) {
		// remove all the events of the last items
		if(this.resultList) {
			for(var i=0; i<this.resultList.length; i++) {
				var item = $(this.resultList[i]);
				item.removeEvents();
			}
		}
		this.resultContainer.innerHTML = result;

		// if container wasn't shown, just call setResultContainerPosition
		if (this.resultContainer.style.display  != "block")
		{
			this.setResultContainerPosition();
		}

		// display the result list
		this.resultContainer.style.display = "block";

		this.resultList = $$('#' + this.hideninput.id + 'autocompleteResultContainer li');
		this.resultList.each(function(item, i) {
			item.addEvent('mouseover', function() {
				if(!this.isFrozen) {
					if(this.currentSelection >= 0) {
						this.resultList[this.currentSelection].removeClass('selected');
					}
					item.addClass('selected');
					this.currentSelection = i;
				}
			}.bind(this));
			item.addEvent('click', this._onItemSelect.bind(this, item));
		}, this);

		// reset the current selection
		this.currentSelection = -1;
		// reset the scroll position
		this.resultContainer.scrollTop = 0;
	},

	_onItemSelect: function(item) {
		if(!this.isFrozen) {
			this.input.value = item.getProperty(this.displayValue);
			this.resultContainer.style.display = "none";
			this.fireEvent('onItemChoose', item);
		}
	}

});

AutoComplete.implement(new Events);
