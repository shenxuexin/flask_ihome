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

$(document).ready(function(){
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

            $(".detail-con").append(template("detail-temp", {house: result.data.house}));
            $(".swiper-pagination").after(template("house-price-temp", {house:result.data.house}));

            if(result.data.user_id !== result.data.house.user_id)
            {
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