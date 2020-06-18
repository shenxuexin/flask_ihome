function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
    $.ajax({
        url: "/api/v1.0/session",
        type: "delete",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        dataType: "json",
        success: function (result) {
            if(result.errno === "0")
            {
                location.href = "/";
            }
            else
            {
                alert("失败");
            }
        }
    })
}

$(document).ready(function(){
    $.get('/api/v1.0/users/profile', function (result) {
        if(result.errno === '0')
        {
            $("#user-avatar").prop("src", result.data.avatar);
            $("#user-name").text(result.data.username);
            $("#user-mobile").text(result.data.mobile);
        }
        else
        {
            alert(result.errmsg);
        }
    })
});