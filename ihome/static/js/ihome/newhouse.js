function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    $.get("/api/v1.0/areas", function (result) {
        if(result.errno === "0")
        {
            var areas = result.data;
            // for(i=0; i<areas.length; i++)
            // {
            //     area = areas[i];
            //     $("#area-id").append("<option value='"+area.id+"'>"+area.name+"</option>");
            // }
            options = template("html_template", {areas:areas});
            $("#area-id").html(options);
        }
    });

    $("#form-house-info").submit(function (e) {
        e.preventDefault();

        var data = {};
        $(this).serializeArray().map(function (x) {
            data[x.name] = x.value;
        });

        var facility = [];
        $(":checked[name='facility']").each(function (index, elem) {
            facility[index] = $(elem).val();
        });

        data.facility = facility;

        $.ajax({
            url: "/api/v1.0/houses/info",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(data),
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (result) {
                if(result.errno === "4101")
                {
                    location.href = "/login.html";
                }
                else if(result.errno === "0")
                {
                    // 隐藏信息表单
                    $("#form-house-info").hide();
                    // 显示图片表单
                    $("#form-house-image").show();
                    // 设置house_id
                    $("#house-id").val(result.data.house_id);
                }
                else
                {
                    alert(result.errmsg);
                }
            }
        })

    });


    $("#form-house-image").submit(function (e) {
        e.preventDefault();

        $(this).ajaxSubmit({
            url: "/api/v1.0/houses/image",
            type: "post",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (result) {
                if(result.errno === "4101")
                {
                    location.href = "/login.html";
                }
                else if(result.errno === "0")
                {
                    $(".house-image-cons").append("<img src='"+result.data.image_url+"'>");
                }
                else
                {
                    alert(result.errmsg);
                }
            }
        });

    });

});