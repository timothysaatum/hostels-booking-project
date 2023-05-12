$(document).ready(function () {
  new WOW().init();
  AOS.init();

  //navbar toogle chevron icons
  $(".toggle").click(function () {
    $(".nav").toggleClass("justify-content-end");
    $(".toggle").toggleClass("text-light");
  });

  $(document).on(
    "click",
    "#apartment, #food, #uds, #knust, #ucc, #legon, #stu, #uenr, #uhas, #tatco, #batco, #cktedam",
    function () {
      const queryValue = $(this).val();
      $.ajax({
        url: "/rooms/",
        type: "GET",
        dataType: "json",
        data: { query: queryValue },
        success: function (hostel) {
          //window.location.href = "/rooms/?response=" + data['query']
          const html = ''
          $(".results").html(hostel);
        },
        error: function (xhr, status, error) {
          console.log(error);
        },
      });
    }
  );
  //sign in and login buttons
  $(".show-div, .search-form").hide();
  $("#account").click(function () {
    $(".show-div").toggle();
  });
  $("#search").click(function () {
    $(".search-form").toggle();
  });
});
