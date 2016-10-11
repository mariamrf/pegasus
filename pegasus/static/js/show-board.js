var isDone;
var canEdit;
var done_at;
var isOwner;
var logged_in;
var username;
var email;
var boardID;
var ALL_TEXT_ELEMENTS = [];


function initVar(isDone, canEdit, done_at, isOwner, logged_in, username, email, boardID){
    isDone = isDone;
    canEdit = canEdit;
    done_at = done_at;
    isOwner = isOwner;
    logged_in = logged_in;
    username = username;
    email = email;
    boardID = boardID;
    // SAVE IMAGE MODAL
    $('#saveImageModal').on('shown.bs.modal', function(){
        $('#save-image-spinner').remove();
        html2canvas(document.getElementById("board-grid"), {
            onrendered: function(canvas){
                document.getElementById("save-image-body").appendChild(canvas);
            }
        });
    });

    $('#saveImageModal').on('hidden.bs.modal', function(){
        $('canvas', this).remove();
        $('#save-image-body').append('<span id="save-image-spinner"><i class="fa fa-pulse fa-spinner"></i></span>');
    });

    // EXPIRATION ICON
    $('#time-until-done').on('mouseover', function(){
        $(this).prop('title', 'loading..');
        var board_done = moment.utc(done_at).local();
        var form = board_done.format("dddd, MMMM Do YYYY, h:mm:ss a");
        if (isDone) {
            $(this).prop('title', 'Expired on ' + form);
        }
        else {
            var toFuture = board_done.fromNow();
            $(this).prop('title', 'Expires ' + toFuture + ".\nOn " + form);
        }
    });

    if (!isOwner && logged_in) {
		$('#remove-thyself').click(function(){
			$('#remove-self-form').submit();
		});

		$('#do-not-remove-thyself').click(function(){
			$('#removeSelfModal').modal('toggle');
		});

		$('#removeSelfModal').on('shown.bs.modal', function(){
			$('#do-not-remove-thyself').focus();
		});
	}

    var INVITE = '-1';
    var temp = getQueryParam('invite'); // so we only call the function once
    if(temp){
        INVITE = temp;
    }
    var me = username;
    var myemail = email;
    var whoami;
    if(!me)
        whoami = myemail;
    else
        whoami = me;
    var colors = {};
    colors[whoami] = '#eee';
    var prevSender = '';
    var lastModified = '0';
    function getMessages(boardID, username, email, isDone, INVITE){
        $.ajax({
            type: 'GET',
            url: Flask.url_for('get_components', {boardID:boardID}),
            data: {
                    'invite': INVITE,
                    'lastModified': lastModified
                },
            success: function(data){
                $('#chat-board-spinner').remove();
                $('#whos-editing').remove();
                // if locked
                if(data.locked){
                    $('#board-grid, #board-tools').addClass('disable');
                    var whoisediting = data.lockedBy;
                    var final_whoisediting = whoisediting;
                    $.ajax({
                            type: 'GET',
                            url: Flask.url_for('get_user', {userID:whoisediting}),
                            async: false, // so we can actually set the username through it
                            dataType: 'json',
                            success: function(d){
                                if(d.error == 'None')
                                    final_whoisediting = d.username;
                            }
                        });
                    $('#board-notice').append('<p class="text-center" id="whos-editing"><span class="whos-editing-name">'+final_whoisediting+'</span> is editing...</p>');
                }
                else{
                    $('#board-grid, #board-tools').removeClass('disable');
                }
                if(!data.error){ // has new messages
                    for(var i=0; i<data.messages.length; i++){
                    var username;
                    console.log(data.messages[i]);
                    if (data.messages[i].userID){
                        var id = data.messages[i].userID; // get username from db
                        $.ajax({
                            type: 'GET',
                            url: Flask.url_for('get_user', {userID:id}),
                            async: false, // so we can actually set the username through it
                            dataType: 'json',
                            success: function(d){
                                if(d.error == 'None'){
                                username = d.username;
                            }
                            else // if username was not found/user was later deleted/etc, though deleting/deactivating should be 'soft'
                                username = id;
                            }
                        });
                    }
                    else
                        username = data.messages[i].userEmail;
                    var time = moment.utc(data.messages[i].created_at).local();
                    var color;
                    if(username==whoami){
                        color = colors[whoami];
                    }
                    else{
                        if(username in colors)
                            color = colors[username];
                        else{
                        var c = randomColor({format: 'rgb'});
                        color = 'rgba'+ c.slice(3,15) + ',0.4)';
                        colors[username] = color;
                        }
                    }
                    if(data.messages[i].type=='chat'){
                        if(username!=prevSender){
                        $('#chat-board').append('<p class="chat-message"> <span class="chat-message-top"><span class="chat-message-date"><i class="fa fa-dot-circle-o"></i></span><span class="chat-username">' + username + '</span>:</span> <span class="chat-message-details" style="background-color:'+color+';" title="'+time.format("dddd, MMMM Do YYYY, h:mm:ss a")+'"></span></p>');
                        }
                        else{
                            $('#chat-board').append('<p class="chat-message followup-message"> <span class="chat-message-details" style="background-color:'+color+';" title="'+time.format("dddd, MMMM Do YYYY, h:mm:ss a")+'"></span></p>');
                        }
                        var list = data.messages[i].content.split('\n');
                        var final = list.join('<br>');
                        $('.chat-message-details').last().html(final);
                        prevSender=username;
                    }
                    else if(data.messages[i].type=='text'){
                        var text_pos = data.messages[i].position;
                        var text_id = data.messages[i].id;
                        var text_content = data.messages[i].content;
                        var list = text_content.split('\n');
                        var final_text_content = list.join('<br>');
                        var exists = false;
                        var isDeleted = data.messages[i].deleted == 'Y' ? true : false;
                        // if modification is deletion and it exists, remove

                        if(isDeleted){
                            $('#text-' + text_id).remove(); // won't do anything if it doesn't exist
                        }
                        else{
                            for(var j=0; j<ALL_TEXT_ELEMENTS.length; j++){
                                var txt = ALL_TEXT_ELEMENTS[j];
                                if(txt.elementID == text_id && txt.content == final_text_content && txt.position == text_pos){
                                    exists = true;
                                    break;
                                }
                            }
                            // why do they snap back to start when moved?
                            // if not:
                            if(!exists){
                                $('#text-' + text_id).remove();
                                // remove from ALL_TEXT_ELEMENTS if it exists, too
                                var txt_n = ALL_TEXT_ELEMENTS.length + 'S';
                                var txt_temp = new TextElement(txt_n, '#board-grid', B, INVITE, CAN_EDIT);
                                txt_temp.init(text_content, text_id, text_pos);
                                ALL_TEXT_ELEMENTS.push(txt_temp);
                            }
                        }
                    }
                    else{
                    // OTHER BOARD CONTENT THAN CHAT
                    // 1 - if it's in the list with the same content and position, don't render it.
                    // 2 - if not, remove if applicable and re-render it.
                    }
                    $("#chat-board").animate({ scrollTop: $('#chat-board').prop("scrollHeight")}, 500);
                    if(data.messages[i].last_modified_at > lastModified)
                            lastModified = data.messages[i].last_modified_at;

                    }
                }
                if(isDone==true){ // no need to undo this anywhere because isDone is final
                    $('#board-grid').addClass('disable');
                }
            } //end success
        });
    }
    if(isDone != true) {
        window.setInterval(getMessages,1000, boardID, username, email, isDone, INVITE);
    }
    else {
        getMessages(boardID); // if it's done, only get messages once, and disable the grid
    }
    initSendMsg(boardID, INVITE);
    $('#chat-textarea').keydown(function(event){ // submit chat when enter alone is pressed
        if(event.keyCode==13 && !event.shiftKey){
            $('#chat-form').submit();
            return false;
        }
    });

    if (isOwner) {
		// SEE INVITED PEOPLE
		$('#invitedUsersModal').on('shown.bs.modal', function(){
			// render list of forms that allows the creator to edit privileges (sp?)
			$.ajax({
				type: 'GET',
				url: Flask.url_for('invited_users', {boardID:boardID}),
				success: function(data){
					$('#invited-users-spinner').remove();
					if(data.error=='None'){
						// we have invited users!
						$('#invited-users-list').append('<div class="invited-users-title">Email <span class="edit-checkbox-title">Can Edit</span></div>');
						for(var i=0; i<data.invited.length; i++){
							var email = data.invited[i].userEmail;
							var type = data.invited[i].type;
							var checked="";
							if(type=='edit'){
								checked="checked";
							}
                            $('#invited-users-list').append('<form class="edit-invited-form">'
                                                            +'<input type="hidden" name="_csrf_token" value="'+data.token+'"/>'
                                                            +'<input type="hidden" name="boardID" value="'+B+'"/>'
                                                            +'<input type="hidden" name="email" value="'+email+'"/>'
                                                            +'<input type="hidden" name="inviteType" value="'+type+'"/>'
                                                            + email
                                                            +'<input name="type" type="checkbox" value="canEdit" aria-label="Enable or disable user\'s editing privileges." title="Can Edit" class="edit-checkbox" '+ checked +'/>'
                                                            +'</form>');
                        }
                        $('.edit-checkbox').bind('change', function(){
                            $(this).parent().submit();
                        });
                        $('.edit-invited-form').submit(function(event){
                            event.preventDefault();
                            $('.edit-checkbox').prop('disabled', true);
                            var d = $(this).serialize();
                            $.ajax({
                                method: 'POST',
                                async: false,
                                url: Flask.url_for('edit_invite'),
                                data: d,
                                success: function(data){
                                    $('.edit-checkbox').prop('disabled', false);
                                    if(data.error != 'None'){
                                        $('#invitedUsersModal .modal-body').prepend('<div class="alert alert-warning" id="error-msg" role="alert">'+data.error+'</div>');
                                    }
                                    $("input[name='_csrf_token']").val(data.token);
                                }
                            });
                        });
                    }
					else {
                        $('#invited-users-list').prepend('<li>'+data.error+'</li>');
					}
				}
			});
		});
		$('#invitedUsersModal').on('hidden.bs.modal', function(){
			$('#invited-users-modal-body').html("<h4 class='text-center' id='invited-users-spinner'><i class='fa fa-spinner fa-pulse'></i></h4>"
				+"<div id='invited-users-list'></div>");
		});

		// DELETE FORM LOGIC
		$('#delete-form').attr('action', Flask.url_for('delete_board', {boardID:boardID}));
		$('#delete-this-board').click(function(){
			$('#delete-form').submit();
		});

		$('#do-not-delete-this-board').click(function(){
			$('#deleteModal').modal('toggle');
		});

		$('#deleteModal').on('shown.bs.modal', function(){
			$('#do-not-delete-this-board').focus();
		});

		// INVITE PEOPLE
        $('#invite-form').bind('submit', function() {
            $('#invite-msg').remove(); // if there were any previous errors
	        var em = $('input[name="email"]').val();
	        $.post(Flask.url_for('invite_user', {email:em, boardID:boardID}), {
	            type: $('input[name="type"]:checked').val(),
	            _csrf_token: $('input[name="_csrf_token"]').val()
	          },
	          function(data) {
	            if(data.successful == 'true'){
	            	$('#inviteModal .modal-body').prepend('<div class="alert alert-success" id="invite-msg" role="alert">Successfully invited!</div>');
	            	document.getElementById("invite-form").reset();
	            }else{
	            	$('#inviteModal .modal-body').prepend('<div class="alert alert-warning" id="invite-msg" role="alert">'+data.error+'</div>')
	            }
	            $('input[name="_csrf_token"]').val(data.token); // replace all tokens in page
	          });
            return false;
        });

        $("#inviteModal").on("hidden.bs.modal", function(){
             document.getElementById("invite-form").reset();
             $('#invite-msg').remove();
        });

	    // EDIT BOARD TITLE
        $('#edit-board-form').bind('submit', function(event){
            event.preventDefault();
            $('#edit-msg').remove(); // if there were any previous errors
            var data = $(this).serialize();
            $.post(Flask.url_for('edit_board', {boardID:B}), data, function(data){
                if(data.error != 'None'){
                    $('#editModal .modal-body').prepend('<div class="alert alert-warning" id="edit-msg" role="alert">' + data.error +'</div>');
                document.getElementById("edit-board-form").reset();
                }
                else{
                    $('#editModal .modal-body').prepend('<div class="alert alert-success" id="edit-msg" role="alert">Successfully changed!</div>');
                    newTitle = $('#title-modal').val();
                    $('#board-title').text(newTitle);
                }
                $('input[name="_csrf_token"]').val(data.token);
            });
        });

        $("#editModal").on("hidden.bs.modal", function(){
             document.getElementById("edit-board-form").reset();
             var nt = $('#board-title').text();
             $('#title-modal').val(nt);
             $('#edit-msg').remove();
        });

		// MARK BOARD AS DONE
        $('#mark-as-done').click(function(){
            $('#mark-as-done-msg').remove();
            var data = $('#mark-as-done-form').serialize();
            $.post(Flask.url_for('mark_done', {boardID:B}), data, function(data){ // make this synchronous?
                $("input[name='_csrf_token']").val(data.token);
                if(data.error=='None'){
                    $('#markAsDoneModal .modal-body').html('<div class="alert alert-success" role="alert">Successfully marked as done!</div>');
                    window.setTimeout(location.reload(), 2000);
                }
                else{
                    $('#markAsDoneModal .modal-body').prepend('<div class="alert alert-warning" id="mark-as-done-msg" role="alert">'+data.error+'</div>');
                }

            });
        });
        $('#do-not-mark-as-done').click(function(){
            $('#markAsDoneModal').modal('toggle');
        });
        $("#markAsDoneModal").on("hidden.bs.modal", function(){
             $('#mark-as-done-msg').remove();
        });
    }

    if (canEdit){
        // ADD TEXT COMPONENT
        $('#tool-add-text').click(function(){
            var n = ALL_TEXT_ELEMENTS.length + 'S'; // softID, position in array + S so no conflicts with the actual component ID
            var temp = new TextElement(n, '#board-grid', B, INVITE, CAN_EDIT);
            temp.create();
            ALL_TEXT_ELEMENTS.push(temp);
        });
    }
};

// GET INVITE CODE IF ANY
function getQueryParam(sParam){
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for(var i=0; i<sURLVariables.length; i++){
        var sParamName = sURLVariables[i].split('=');
        if(sParamName[0].toLowerCase() == sParam.toLowerCase()){
            return sParamName[1];
        }
    }
}
function initSendMsg(boardID, INVITE){
    $('#chat-form').bind('submit', function(event){
        event.preventDefault();
        var message = $('#chat-textarea').val();
        if(!message)
            return false;
        $('#chat-textarea').prop('disabled', true); // disable the textarea once we send
        $.ajax({
            async: false,
            type: 'POST',
            url: Flask.url_for('post_components', {boardID:boardID}),
            data: {
            '_csrf_token': $("input[name='_csrf_token']").val(),
            'invite': INVITE,
            'position': 'None', // chat messages don't have positions on board
            'message': message,
            'content-type': 'chat'
            },
            success: function(data){
                if(data.error != 'None'){
                    $('#board-error').remove();
                    $('#board-header').append('<div class="alert alert-warning" id="board-error" role="alert">'+data.error+'</div>');
                }
                $("input[name='_csrf_token']").val(data.token);
                $('#chat-textarea').val('');
            },
            error: function(message){
                console.log(message);
            }
        }).always(function(){
            $('#chat-textarea').prop('disabled', false); // re-enable once everything is done and tokens are re-assigned
        });
    });
}