var curPage = 1;
var nextPage = 1;
var totalPage = 1;
var dataQuering = false;


function decodeQuery() {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}


function updateFilterDateDisplay() {
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var $filterDateTitle = $(".filter-title-bar>.filter-title").eq(0).children("span").eq(0);
    if (startDate) {
        var text = startDate.substr(5) + "/" + endDate.substr(5);
        $filterDateTitle.html(text);
    } else {
        $filterDateTitle.html("入住日期");
    }
}

function updateHouseData(action="append"){
    var areaId = $(".filter-area>li.active").attr("area-id");
    if(areaId === undefined) areaId = "";
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var sortKey = $(".filter-sort>li.active").attr("sort-key");
    var params = {
        "sd": startDate,
        "ed": endDate,
        "sk": sortKey,
        "aid": areaId,
        "page": nextPage
    };


    $.get("/api/v1.0/houses", params, function (result) {
        dataQuering = false;
        totalPage = result.data.total_page;
        if(result.errno === "0") {
            if(result.data.total_page === 0)
            {
                $(".house-list").html("暂时没有符合条件的房屋");
            }
            else
            {
                if(action === "renew")
                {
                    curPgae = 1;
                    $(".house-list").html(template("house-list-temp", {houses: result.data.houses}));
                }
                else
                {
                    curPage = nextPage;
                    $(".house-list").append(template("house-list-temp", {houses: result.data.houses}));
                }
            }
        }
    })
}


$(document).ready(function(){
    var queryData = decodeQuery();
    var startDate = queryData["sd"];
    var endDate = queryData["ed"];
    $("#start-date").val(startDate); 
    $("#end-date").val(endDate); 
    updateFilterDateDisplay();
    var areaName = queryData["aname"];
    var areaId = queryData['aid'];
    if (!areaName) areaName = "位置区域";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);

    template("house-list-temp", {house:[]});

    // 获取区域信息
    $.get("/api/v1.0/areas", function (result) {
        if(result.errno === "0")
        {
            $(".filter-area").html(template("filter-area-temp", {areas: result.data}));
            $(".filter-area>li").each(function () {
                if($(this).attr("area-id") === areaId)
                {
                    $(this).addClass("active").siblings().removeClass("active");
                }
            });

            updateHouseData("renew");
        }
    });


    var windowHeight = $(window).height();
    window.onscroll = function(){
        var scrollTop = document.documentElement.scrollTop === 0? document.body.scrollTop:document.documentElement.scrollTop;
        var scrollHeight = document.documentElement.scrollHeight === 0? document.body.scrollHeight:document.documentElement.scrollHeight;

        if(scrollHeight-scrollTop < windowHeight+50)
        {
            if(!dataQuering)
            {
                dataQuering = true;
                if(curPage < totalPage)
                {
                    nextPage = curPage+1;
                    updateHouseData();
                }
                else
                {
                    dataQuering = false;
                }
            }

        }
    };

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    var $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function(e){
        var index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
        }
    });
    $(".display-mask").on("click", function(e) {
        $(this).hide();
        $filterItem.removeClass('active');
        updateFilterDateDisplay();
        curPage = 1;
        nextPage = 1;
        totalPage = 1;
        updateHouseData("renew");
    });
    $(".filter-item-bar>.filter-area").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
    });
    $(".filter-item-bar>.filter-sort").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
        }
    })
});