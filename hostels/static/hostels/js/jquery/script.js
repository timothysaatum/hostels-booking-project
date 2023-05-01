$(document).ready(function () {
  new WOW().init();
  AOS.init();

  //just dey play
  $(".toggle").click(function () {
    $(".nav").toggleClass("justify-content-end");
    $(".toggle").toggleClass("text-light");
  });

  //displaying user login, logout and create account on click
  $("#account").click(function () {
    $("#show").toggle(500);
  });

  $("#apartment, #food, #uds, #knust, #ucc, #legon, #stu, #uenr, #uhas, #tatco, #batco, #cktedam").click(function () {
    const queryValue = $(this).val();
    console.log(queryValue)
    $.ajax({
      url: "/rooms/",
      type: "GET",
      data: { query: queryValue },
      success: function (response) {
        //window.location.href = "/rooms/?response=" + encodeURIComponent(response);
        $(".content").html(response);
      },
      error: function (xhr, status, error) {
        console.log(error);
      }
    });
  });
});