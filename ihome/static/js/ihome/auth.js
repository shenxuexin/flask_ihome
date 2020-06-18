function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function () {
    $.get("/api/v1.0/users/auth", function (result) {
        if(result.errno === "0")
        {
            $("#real-name").val(result.data.real_name);
            $("#id-card").val(result.data.id_card);
        }
        else
        {
            alert(result.errmsg);
        }
    });

    $("#form-auth").submit(function (e) {
        e.preventDefault();

        $(this).ajaxSubmit({
            url: "api/v1.0/users/auth",
            type: "post",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (result) {
                alert(result.errmsg);
            }
        });



    });

});
