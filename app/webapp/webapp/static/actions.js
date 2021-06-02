

var getToken = function() {
    $.ajax({
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        url: '/token',
        // The data sent to the Django view in JSON format
        data: JSON.stringify({
            formField: $('#body').val()
        }),
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            alert("Error: "+ errorThrown);
        },
        success: function (data) {
            console.log(data);
            console.log(data.token);
            $('#token_box').html("Token: " + data.token)
            $('#expires_box').html("Expires: " + data.expires)
        }
    });
}

$('a.logout').click(function(event) {
    var href = this.href;
    event.preventDefault();
    var host = window.location.hostname;
    var domain = host.includes('.') ?  host.slice(host.indexOf('.')) : host;
    document.cookie = 'sage_username=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=' + domain;
    document.cookie = 'sage_uuid=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=' + domain;
    document.cookie = 'sage_token=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=' + domain;
    document.cookie = 'sage_token_exp=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=' + domain;
    document.cookie = 'portal_redirect=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/';
    window.location = href;
});
