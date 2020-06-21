$(document).ready(function(){
    $.get("/api/v1.0/users/auth", function (result) {
        if(result.errno === "4101")
        {
            location.href = "/login.html";
        }
        else if(result.errno === "0")
        {
            if(!(result.data.real_name && result.data.id_card))
            {
                $(".auth-warn").show();
                $("#houses-list").hide();
            }
            else
            {
                $.get("/api/v1.0/user/houses", function (result) {
                    if(result.errno === "4101")
                    {
                        location.href = "/login.html";
                    }
                    else if(result.errno === "0")
                    {
                        $("#houses-list").append(template("house-list-temp", {"houses":result.data}));
                        console.log(template("house-list-temp", result.data))
                    }
                    else
                    {
                        $("#houses-list").append(template("house-list-temp", {"houses": []}));
                    }
                })
            }
        }
        else
        {

        }
    });

});