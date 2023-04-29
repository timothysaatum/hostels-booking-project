$(document).ready(function () {
  new WOW().init();
  AOS.init();

  $(window).on("scroll", function () {
    $(".bg-onscroll").css("background-color", "white");
  });
  //just dey play
  $(".toggle").click(function () {
    $(".nav").toggleClass("justify-content-end");
    $(".toggle").toggleClass("text-light");
  });
});