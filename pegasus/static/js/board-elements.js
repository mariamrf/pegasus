// TEXT
var TextElement = function(softID, canvasID, boardID, invite){
	this.softID = softID;
	this.canvasID = canvasID;
	this.boardID = boardID;
	this.invite = invite;
	this.elementID = ''; // empty for now
	this.create = function(){
		var self = this;
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
	this.save = function(message, type, id){
		var self = this;
		var URL;
		if(type=='create')
			URL = Flask.url_for('board_components', {boardID:self.boardID});
		else 
			URL = Flask.url_for('edit_component', {boardID:self.boardID, componentID:id});

		$.ajax({
			method: 'POST',
			async: false,
			url: URL,
			data:{
				'_csrf_token': $("input[name='_csrf_token']").val(),
				'invite': self.invite,
				'content-type': 'text',
				'message': message
			},
			success: function(data){
				if(data.error == 'None'){
					var formSelector = '#text-'+type+'-form-'+id;
					$(formSelector).remove();
					if(type=='create'){
						self.elementID = data.componentID;
						$(self.canvasID).prepend('<span class="draggable-text" id="text-'+self.elementID+'"></span>');
					}
					var list = message.split('\n');
					var final = list.join('<br>');
					$('#text-'+self.elementID).html(final);
					if(type=='create'){
						$('#text-' + self.elementID).draggable({
							containment: self.canvasID,
							cursor: 'move'
						});

						$('#text-' + self.elementID).dblclick(function(){
							var v = $(this).text(); // this won't render line breaks so fix it
							$(this).html('<form id="text-edit-form-'+self.elementID
										+'"><textarea id="text-edit-'+self.elementID
										+'" name="message" class="text-edit-input">'+v+'</textarea></form>');
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
						});
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
};