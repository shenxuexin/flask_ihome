function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, "").split("&").reduce(function(result, item){
        values = item.split("=");
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(function(){
    var house_id = decodeQuery()["id"];
    $.get("/api/v1.0/houses/"+house_id, function (result) {
        if(result.errno === "0")
        {
            if(result.data.house.max_days === 0)
            {
                result.data.house.max_days = "无限制";
            }
            $(".swiper-wrapper").append(template("slide-list-temp", {images: result.data.house.images}))
            var mySwiper = new Swiper (".swiper-container", {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: ".swiper-pagination",
                paginationType: "fraction"
            });

            var house = result.data.house;
            $(".swiper-pagination").after(template("house-price-temp", {house:result.data.house}));

            // 获取全部设施
            $.get("/api/v1.0/facilities", function (result) {
                if(result.errno === "0")
                {
                    var facilities = result.data;
                    var facilities_exist = house.facilities;
                    var len1 = facilities.length;
                    var len2 = facilities_exist.length;

                    // 过滤当前房屋存在的设施
                    var compare = 0;
                    for(var i=0; i<len1; i++)
                    {
                        if(compare >= len2)
                        {
                            break;
                        }

                        for(var j=0; j<len2; j++)
                        {
                            if(facilities[i].id === facilities_exist[j])
                            {
                                facilities[i].exist = true;
                                compare ++;
                            }
                        }
                    }

                    $(".detail-con").append(template("detail-temp", {house:house, facilities:facilities}));
                }
            });

            if(result.data.user_id !== result.data.house.user_id)
            {
                $(".book-house").attr("href", "/booking.html?hid="+result.data.house.id);
                $(".book-house").show();
            }
            else
            {
                $(".book-house").hide();
            }
        }
    });


    $(".book-house").show();
});