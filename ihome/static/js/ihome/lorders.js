//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // 请求订单数据
    $.get("/api/v1.0/orders", {role: "landlord"}, function (result) {
        if(result.errno === "4101")
        {
            location.href = "/login.html";
        }
        else if(result.errno === "0")
        {
            $(".orders-list").html(template("orders-list-temp", {orders: result.data}));
            $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
            $(window).on('resize', centerModals);
            $(".order-accept").on("click", function(){
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-accept").click(function () {
                    $.ajax({
                        url: "/api/v1.0/order/"+orderId+"/status",
                        type: "put",
                        contentType: "application/json",
                        headers: {
                            "X-CSRFToken": getCookie("csrf_token")
                        },
                        data: JSON.stringify({action: "accept"}),
                        dataType: "json",
                        success: function (result) {
                            if(result.errno === "4101")
                            {
                                location.href = "/login.html";
                            }
                            else if(result.errno === "0")
                            {
                                location.reload();
                            }
                            else
                            {
                                alert(result.errmsg);
                            }
                        }
                    })
                });

            });

            $(".order-reject").on("click", function(){
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-reject").click(function () {
                    var reason = $("#reject-reason").val();

                    if (reason.length === 0)
                    {
                        alert("拒单原因不能为空");
                    }
                    else
                    {
                        $.ajax({
                            url: "/api/v1.0/order/"+orderId+"/status",
                            type: "put",
                            contentType: "application/json",
                            headers: {
                                "X-CSRFToken": getCookie("csrf_token")
                            },
                            data: JSON.stringify({action: "reject", reason: reason}),
                            dataType: "json",
                            success: function (result) {
                                if(result.errno === "4101")
                                {
                                    location.href = "/login.html";
                                }
                                else if(result.errno === "0")
                                {
                                    location.reload();
                                }
                            }
                        })
                    }


                });
            });
        }
    });




});