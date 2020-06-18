function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    $("#form-avatar").submit(function (e) {
        e.preventDefault();

        $(this).ajaxSubmit({
            url: "/api/v1.0/users/avatar",
            type: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            dataType: 'json',
            success: function (result) {
                if(result.errno === "0")
                {
                    var avatarUrl = result.data.avatar_url;
                    $("#user-avatar").prop('src', avatarUrl);
                }
                else
                {
                    alert(result.errmsg);
                }
            }
        });
    });
});
