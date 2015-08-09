(function($) {
    $(document).ready(function($) {
    	// check if history link exists in site, if yes, we are on the user detail site and don't want to include the button
    	if ($(".historylink").length == 0) {
    		// check if .object-tools exists
	    	if ($(".object-tools").length == 0) {
	    		$("#content-main").prepend('<ul class="object-tools"><li><a class="addlink" href="/admin/auth/user/import_users/">Import all users from User Backend</a></li></ul>');
	    	} else {
	        	$(".object-tools").prepend('<li><a class="addlink" href="/admin/auth/user/import_users/">Import all users from User Backend</a></li>');
	        	}
    	}
    	
    });
})(django.jQuery);
