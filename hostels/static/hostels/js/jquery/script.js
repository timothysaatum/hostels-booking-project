$(document).ready(function () {
  new WOW().init();
  AOS.init();

  //navbar toogle chevron icons
  $(".toggle").click(function () {
    $(".nav").toggleClass("justify-content-end");
    $(".toggle").toggleClass("text-light");
  });

  //displaying user login, logout and create account on click
  $("#account").click(function () {
    $("#show").toggle(500);
  });

  $(document).on('click', "#apartment, #food, #uds, #knust, #ucc, #legon, #stu, #uenr, #uhas, #tatco, #batco, #cktedam", function () {
    const queryValue = $(this).val();
    $.ajax({
      url: "/rooms/",
      type: "GET",
      data: { query: queryValue },
      success: function (hostel) {
        //window.location.href = "/rooms/?response=" + encodeURIComponent(response);
        $(".content").html(hostel);
      },
      error: function (xhr, status, error) {
        console.log(error);
      },
    });
  });
});
