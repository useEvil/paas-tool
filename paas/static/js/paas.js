var noAlert = true;
var isOpen  = false;
var timeOut = 12000;
var tID     = '';
var formID  = '';
var shown   = [ ];
var dLong   = 'yyyy-M-d HH:mm:ss';
var dShort  = 'yyyy-M-d';

/* Events */
$('.submit_create').live('click', submitCreateForm);
$('.submit_login').live('click', submitLoginForm);
$('.cancel_create').live('click', cancelCreateForm);
$('.cancel_login').live('click', cancelForm);
$('.approve_release').live('click', approveReleaseList);
$('#approve_release').live('click', approveRelease);
$('#releaseEnvironment').live('change', getEnvironments);
$('#releaseProject').live('click', getBuilds);


/* Binds */
$('body').keyup(cancelOverlay);
$(window).bind('resize',showOverlayBox);

$(document).ready(function() {
    clearMessage();
    if ((window.location.href.indexOf('login') > -1) || (window.location.href.indexOf('create') > -1)) {
        initDatePickers();
        getProjects();
    }
});

var toggleContent = function(e) {
    if ($('#details_'+this.id).css('display') == 'none') {
        $('#details_'+this.id).slideDown(300);
    } else {
        $('#details_'+this.id).slideUp(300);
    }
    return false;
};


/* Init Functions */
function initDatePickers() {
    $('#releaseDate').datetime(/*{ defaultDate: startDate, maxDate: endDate }*/)
}


/* Overlay Functions */
function clearMessage(out) {
    if (!out) out = timeOut;
    tID = setTimeout(function(){ $('#message').html('') }, out);
}

function showOverlay(overlay) {
    if (tID) clearTimeout(tID);
    if (!overlay) overlay = 'overlay';
    $('#'+overlay).css('display', 'block');
    $('#'+overlay).height($(document).height());
    $('#message').css('color','#000000');
    $('#message').css('margin-left','10px');
    $('#message').css('font-weight','bold');
    $('#message').html('Loading...Please Wait!');
}

function showOverlayBox(overlay, layer) {
    //if box is not set to open then don't do anything
    if (isOpen == false) return;
    // set the properties of the overlay box, the left and top positions
    $(overlay).css({
        display: 'block',
        left: ($('#middle').width() - $(overlay).width())/2,
        top: $(window).scrollTop()+50,
        position: 'absolute'
    });
    // set the window background for the overlay. i.e the body becomes darker
    if (layer) {
        $('.background-cover-top').css({
            display: 'block',
            width: '100%',
            height: $(document).height()
        });
        $(overlay).css({ 'z-index': $(overlay).css('z-index')+layer });
    } else {
        $('.background-cover').css({
            display: 'block',
            width: '100%',
            height: $(document).height()
        });
    }
}

function hideOverlay(overlay, out) {
    if (!overlay) overlay = 'overlay';
    $('#'+overlay).css('display', 'none');
    clearMessage(out);
}

function doOverlayOpen(overlay, layer) {
    overlay = '#overlay-box-'+overlay;
    //set status to open
    isOpen = true;
    showOverlayBox(overlay, layer);
    if (layer) {
        $('.background-cover-top').css({opacity: 0}).animate({opacity: 0.5, backgroundColor: '#000'});
    } else {
        $('.background-cover').css({opacity: 0}).animate({opacity: 0.5, backgroundColor: '#000'});
    }
    // dont follow the link : so return false.
    return false;
}

function doOverlayClose(overlay, layer) {
    overlay = '#overlay-box-'+overlay;
    //set status to closed
    isOpen = false;
    $(overlay).css('display', 'none');
    // now animate the background to fade out to opacity 0
    // and then hide it after the animation is complete.
    if (layer) {
        $('.background-cover-top').animate( {opacity: 0}, 'fast', null, function() { $(this).hide(); } );
        $(overlay).css({ 'z-index': $(overlay).css('z-index')-layer });
    } else {
        $('.background-cover').animate( {opacity: 0}, 'fast', null, function() { $(this).hide(); } );
    }
}

function doOverlaySwap(close_overlay, open_overlay) {
    // close the current overlay
    overlay = '#overlay-box-'+close_overlay;
    //set status to closed
    isOpen = false;
    $(overlay).css('display', 'none');
    // open the next overlay
    overlay = '#overlay-box-'+open_overlay;
    //set status to open
    isOpen = true;
    showOverlayBox(overlay);
    return false;
}


/* Main Functions */
function cancelOverlay(e) {
    var keyCode;
    if (e == null) {
        keyCode = event.keyCode;
    } else { // mozilla
        keyCode = e.which;
    }
    if (keyCode == 27) {
        if (formID.match('_form')) {
            $('#'+formID+' .cancel_button').trigger('click');
        } else {
            $('#'+formID+'_form .cancel_button').trigger('click');
        }
        formID  = '';
    }
}

function cancelEditForm(event, id) {
    var element = id ? id : this.id;
    var display = element.replace('cancel_', '');
    $('#'+display+'_form').find('input').each(function(){
        if ($(this).attr('type') == 'text') $(this).attr('value', '');
        if ($(this).attr('type') == 'checkbox') $(this).attr('checked', false);
        if ($(this).attr('type') == 'radio') $(this).attr('checked', false);
    });
    $('#'+display+'_form').find('textarea').each(function(){
        $(this).attr('value', '');
    });
    $('#'+display+'_form').find('select').each(function(){
        $(this).children().each(function(){
            if ($(this).val() == 0) {
                $(this).attr('selected', true);
            } else {
                $(this).attr('selected', false);
            }
        });
    });
    $('#'+display+'_form').find('label').each(function(){
        $(this).css('color', '#000000');
    });
    $('#'+display+'_form').hide();
    doOverlayClose(display);
}

function cancelCreateForm(event) {
    window.location.href = '/';
}

function cancelForm(event, id) {
    var classId = id ? id : this.id;
    var parts   = classId.split('_');
    var display = parts[1];
    doOverlayClose(display);
}

function submitCreateForm(event, id) {
    var classId = id ? id : this.id;
    var parts   = classId.split('_');
    var display = parts[1];
    if (validateForm(display, id)) {
        return false;
    } else {
        $('#releaseStatus').attr('disabled', false);
    }
    var params  = $('#'+display+'_form').serialize();
    doOverlayOpen('loading');
    $.ajax(
        {
            url: '/REST/release/create',
            type: 'post',
            data: params,
            timeout: 10000,
            error: failedCreateForm,
            success: updateCreateForm,
        }
    );
}

function submitLoginForm(event, id) {
    var classId = id ? id : this.id;
    var parts   = classId.split('_');
    var display = parts[1];
    if (validateForm(display, id)) {
        return false;
    }
    var params  = $('#'+display+'_form').serialize();
    doOverlayOpen('loading', 25);
    $.ajax(
        {
            url: '/REST/release/login',
            type: 'post',
            data: params,
            timeout: 10000,
            error: failedLoginForm,
            success: updateLoginForm,
        }
    );
}

function showCreatePage(event) {
    window.location.href = '/create';
}

function showLoginForm(event) {
    doOverlayOpen('login');
}

function showListing(event) {
    window.location.href = '/';
}

function showReports(event) {
    window.location.href = '/reports';
}

function failedCreateForm(data) {
    if (data['status'] == 500) data['message'] = data['status'] + ': ' + data['statusText'];
    doOverlayClose('loading', 25);
    $('#releaseStatus').attr('disabled', true);
    updateStatus(data);
}

function failedLoginForm(data) {
    if (data['status'] == 500) data['message'] = data['status'] + ': ' + data['statusText'];
    doOverlayClose('login');
    updateStatus(data);
}

function updateCreateForm(data) {
    doOverlayClose('loading');
    updateStatus(data);
    if (data['status'] != 200) return;
    window.location.replace('/');
}

function updateLoginForm(data) {
    doOverlayClose('loading', 25);
    doOverlayClose('login');
    updateStatus(data);
    $('#login_form').find('input').each(function(){
        if ($(this).attr('type') == 'password') this.value = '';
    });
    if (data['status'] != 200) return;
}

function updateApproveStatus(data) {
    doOverlayClose('loading');
    updateStatus(data);
    if (data['status'] != 200) return;
    $('#approvedBy').attr('value', data['userId']);
    $('#approvedBy').show();
    $('#approve_release').hide();
}

function updateApproveStatusList(data) {
    doOverlayClose('loading');
    updateStatus(data);
    if (data['status'] != 200) return;
    window.location.replace('/');
}

function updateProjectList(data) {
    doOverlayClose('loading');
    var varId = $('#releaseProject');
    varId.children().each(function(){
        $(this).remove();
    });
    for (key in data) {
        var option = new Option(data[key], data[key]);
        varId.append(option);
    }
}

function updateEnvironmentList(data) {
    doOverlayClose('loading');
    var varId = $('#releaseDeployable');
    varId.children().each(function(){
        $(this).remove();
    });
    for (key in data) {
        var option = new Option(data[key], data[key]);
        varId.append(option);
    }
}

function updateBuildList(data) {
    doOverlayClose('loading');
    var varId = $('#releaseVersion');
    varId.children().each(function(){
        $(this).remove();
    });
    for (key in data) {
        var build  = data[key].join('-');
        var option = new Option(build, build);
        varId.append(option);
    }
    updateRollbackList(data);
}

function updateRollbackList(data) {
    doOverlayClose('loading');
    var varId = $('#releaseRollback');
    varId.children().each(function(){
        $(this).remove();
    });
    for (key in data) {
        var build  = data[key].join('-');
        var option = new Option(build, build);
        varId.append(option);
    }
}

function updateStatus(data) {
//          //alert("updateStatus ");
    if (tID) clearTimeout(tID);
    var status_msg = $('#message');
    if (data['status'] != 200) {
        status_msg.css('color','red');
    } else {
        status_msg.css('color','green');
    }
    status_msg.html(data['message']);
    clearMessage();
}

function logMeIn(data) {
    alert('logMeIn');
}

function validateForm(object, id) {
    var required = new Array('Project', 'Date', 'Version', 'Login', 'Password');
    var title    = 'Release Info ';
    var error    = false;
    if (object == 'login') {
        required = new Array('Login', 'Password');
        title    = 'Login Info ';
    }
    for (key in required) {
        var field    = required[key].replace(/ /g, '');
        var value    = $('#release'+field).val();
        var selected = $('#release'+field+' option:selected');
        if (selected.val()) value = selected.val();
        if (!value) {
            $('#release'+field+'Label').css('color', '#FF0000');
            message = {
                'status': 404,
                'message': title +required[key]+' is Required'
            };
            updateStatus(message);
            error = true;
        } else {
            $('#release'+field+'Label').css('color', '#000000');
        }
    }
    return error;
}

function approveRelease(event) {
    doOverlayOpen('loading');
    $.getJSON('/REST/release/approve/'+$('#releaseId').val(), updateApproveStatus);
}

function approveReleaseList(event, id) {
    var itemId = id ? id : this.id;
    var parts  = itemId.split('_');
    var releaseId = parts[1];
    doOverlayOpen('loading');
    $.getJSON('/REST/release/approve/'+releaseId, updateApproveStatusList);
}

function getProjects(event, id) {
    var itemId = id ? id : this.id;
    var selected = $('#'+itemId+' option:selected');
    doOverlayOpen('loading');
    $.getJSON('/REST/release/projects', updateProjectList);
}

function getEnvironments(event, id) {
    var selected = $('#releaseProject option:selected');
    doOverlayOpen('loading');
    $.getJSON('/REST/release/environments/'+selected.val(), updateEnvironmentList);
}

function getBuilds(event, id) {
    var itemId = id ? id : this.id;
    var selected = $('#'+itemId+' option:selected');
    doOverlayOpen('loading');
    $.getJSON('/REST/release/builds/'+selected.val(), updateBuildList);
}
