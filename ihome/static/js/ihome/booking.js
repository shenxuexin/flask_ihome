function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function(){
    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });

    var queryData = decodeQuery();
    var houseId = queryData["hid"];

    // 显示房屋信息
    $.get("/api/v1.0/houses/"+houseId, function (result) {
        if(result.errno === "0")
        {
            $(".house-info>img").attr("src", result.data.house.image_url);
            $(".house-text>h3").text(result.data.house.title);
            $(".house-text span").text(result.data.house.price);
        }
    });

    // 点击事件
    $(".submit-btn").click(function () {
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();
        // console.log(houseId);
        var params = {
            "house_id": houseId,
            "start_date": startDate,
            "end_date": endDate
        };

        $.ajax({
            url: "/api/v1.0/orders",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
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
                    location.href = "/orders.html";
                }
                else
                {
                    alert(result.errmsg);
                }
            }
        });

    });

    $(".input-daterange").on("changeDate", function(){
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg();
        } else {
            var sd = new Date(startDate);
            var ed = new Date(endDate);
            days = (ed - sd)/(1000*3600*24) + 1;
            var price = $(".house-text>p>span").html();
            var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共"+ days +"晚)");
        }
    });
});
