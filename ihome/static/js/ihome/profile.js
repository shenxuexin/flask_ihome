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
    $.get("api/v1.0/user", function (result) {
        if(result.errno === "0")
        {
            if(result.data.avatar !== null){
                $("#user-avatar").prop("src", result.data.avatar);
            }
            $("#user-name").val(result.data.username);
        }
    });


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
                    $(".error-msg").hide();
                    showSuccessMsg();
                }
                else if(result.errno === "4101")
                {
                    location.href = "/login.html";
                }
                else
                {
                    $(".error-msg").text(result.errmsg);
                    $(".error-msg").show();
                }
            }
        });
    });


    $("#form-name").submit(function (e) {
        e.preventDefault();

        var send_data = {
            "username": $("#user-name").val()
        };

        var send_json = JSON.stringify(send_data);

        $.ajax({
            url: "/api/v1.0/users/name",
            type: "put",
            data: send_json,
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            contentType: "application/json",
            success: function (result) {
                if(result.errno === "0")
                {
                    $(".error-msg").hide();
                    showSuccessMsg();
                }
                else if(result.errno === "4101")
                {
                    location.href = "/login.html";
                }
                else
                {
                    $(".error-msg").text(result.errmsg);
                    $(".error-msg").show();
                }
            }
        })

    });
});
