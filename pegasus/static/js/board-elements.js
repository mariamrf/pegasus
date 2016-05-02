// TEXT
var TextElement = function(softID, canvasID, boardID, invite, canEdit){ // canEdit is boolean
	this.content = '';
	this.softID = softID;
	this.canvasID = canvasID;
	this.boardID = boardID;
	this.invite = invite;
	this.elementID = ''; // empty for now
	this.editable = canEdit;
	this.position = JSON.stringify({"top": 0, "left": 0});
	this.init = function(message, id, pos){
		var self = this;
		self.elementID = id;
		self.position = pos;
		var jsonParse = JSON.parse(self.position);
		$(self.canvasID).prepend('<span class="draggable-text" id="text-'+self.elementID+'"></span>');
		var list = message.split('\n');
		var final = list.join('<br>');
		self.content = final;
		$('#text-'+self.elementID).html(final);
		$('#text-'+self.elementID).css(jsonParse);
		if(self.editable){
			$('#text-' + self.elementID).draggable({
				containment: self.canvasID,
				cursor: 'move',
				stop: function(event, ui){
					self.refresh(ui.position);
				}
			});
			function hoverEnterEvent(){
				$('#text-delete-form-'+self.elementID).remove();
				$(this).prepend('<form class="delete-form" id="text-delete-form-'+self.elementID
							+'"><button type="submit" class="global-btn delete-btn" title="Delete Text" id="delete-'+self.elementID
							+'"><i class="fa fa-trash"></i></button></form>');
				$('#text-delete-form-'+self.elementID).bind('submit', function(event){
					event.preventDefault();
					var id = self.elementID;
					var csrf = $("input[name='_csrf_token']").val();
					var invite = self.invite;
					var url = Flask.url_for('delete_component', {boardID:self.boardID, componentID:id});
					$.ajax({
						async: false,
						method: 'POST',
						url: url,
						data: {
							'_csrf_token': csrf,
							'invite': invite
						},
						success: function(data){
							if(data.error == 'None'){
								$('#text-' + self.elementID).remove();
							}
							else{
								$(self.canvasID).prepend('<div id="board-error" class="alert alert-warning">'
												+'<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'
												+'<strong>Error: </strong>'+data.error+'</div>');
							}
							$("input[name='_csrf_token']").val(data.token);
						}
					});
				});
			}
			function hoverLeaveEvent(){
				$('#text-delete-form-'+self.elementID).remove();
			}
			function doubleClickEvent(){
				var v = $(this).text(); // this won't render line breaks so fix it
				$(this).html('<form id="text-edit-form-'+self.elementID
							+'"><textarea id="text-edit-'+self.elementID
							+'" name="message" class="text-edit-input">'+v+'</textarea></form>');
				$('#text-edit-'+self.elementID).focus();
				$('#text-edit-'+self.elementID).bind('blur', function(){
					$('#text-edit-form-'+self.elementID).submit();
				});
				$('#text-edit-'+self.elementID).keydown(function(event){
					if(event.keyCode==13 && !event.shiftKey){
						$('#text-edit-form-'+self.elementID).submit();
						return false;
					}
				});
				$('#text-edit-form-'+self.elementID).bind('submit', function(event){
					event.preventDefault();
					var val = $('#text-edit-'+self.elementID).val();
					self.save(val, 'edit', self.elementID);
				});

			}
			$('#text-' + self.elementID).dblclick(doubleClickEvent);
			// double tap event would go here

			$('#text-' + self.elementID).hover(hoverEnterEvent, hoverLeaveEvent);
			// single tap event would go here
		}

	}
	this.create = function(){
		var self = this;
		if(self.editable){
			$(self.canvasID).prepend('<form id="text-create-form-'+self.softID+'">'
								+'<textarea name="message" id="text-create-'+self.softID+'" class="text-create-input"></textarea>'
								+'</form>');
			$('#text-create-'+self.softID).focus();
			$('#text-create-'+self.softID).bind('blur', function(){
				$('#text-create-form-'+self.softID).submit();
			});
			$('#text-create-'+self.softID).keydown(function(event){
				if(event.keyCode==13 && !event.shiftKey){
						$('#text-create-form-'+self.softID).submit();
						return false;
					}
			});
			$('#text-create-form-'+self.softID).bind('submit', function(event){
				event.preventDefault();
				var val = $('textarea[name="message"]', this).val();
				self.save(val, 'create', self.softID);
			});
		}
		
	}
	this.save = function(message, type, id, pos){
		var self = this;
		if(self.editable){
			var URL;
			if(type=='create'){
				URL = Flask.url_for('post_components', {boardID:self.boardID});
				position = self.position;
			}
			else{
				URL = Flask.url_for('edit_component', {boardID:self.boardID, componentID:id});
				position = ''; // won't actually be handled in any way server-side since this 'hasMessages'
			}

			$.ajax({
				method: 'POST',
				async: false,
				url: URL,
				data:{
					'_csrf_token': $("input[name='_csrf_token']").val(),
					'invite': self.invite,
					'content-type': 'text',
					'hasMessages': 'true',
					'message': message,
					'position': position
				},
				success: function(data){
					if(data.error == 'None'){
						var formSelector = '#text-'+type+'-form-'+id;
						$(formSelector).remove();
						if(type=='create'){
							self.init(message, data.componentID, position);
						}
						else{
							var list = message.split('\n');
							var final = list.join('<br>');
							$('#text-'+self.elementID).html(final);
							self.content = final;
						}
					}
					else{
						$(self.canvasID).prepend('<div id="board-error" class="alert alert-warning">'
												+'<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'
												+'<strong>Error: </strong>'+data.error+'</div>');
					}
					$("input[name='_csrf_token']").val(data.token);
				}
			});
		}	
	}
	this.refresh = function(position){
		var self = this;
		if(self.editable){
			var posToString = JSON.stringify(position);
			self.position = posToString;
			$.ajax({
				method: 'POST',
				url: Flask.url_for('edit_component', {boardID:self.boardID, componentID:self.elementID}),
				async: false,
				data:{
					'_csrf_token': $("input[name='_csrf_token']").val(),
					'invite': self.invite,
					'content-type': 'text',
					'hasMessages': 'false',
					'position': posToString
				},
				success: function(data){
					if(data.error == 'None'){
						console.log("Successfully updated position!");
					}
					else{
						$(self.canvasID).prepend('<div id="board-error" class="alert alert-warning">'
												+'<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'
												+'<strong>Error: </strong>'+data.error+'</div>');
					}
					$("input[name='_csrf_token']").val(data.token);
				}
			});
		}
	}
};