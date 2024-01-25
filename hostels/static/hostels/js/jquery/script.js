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
        url: "/",
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
  $(".show-div, .search-form, .show-btn, .empty-rooms").hide();
  $("#account").click(function () {
    $(".show-div").toggle();
  });
  $("#search").click(function () {
    $(".search-form").toggle();
  });

  $(".booking-button").click(function(){
    alert(this).attr('id')
  });
  //confirmation button click
  $('#confirmation').click(function(){
    $(".show-btn").toggle()
    $("#confirmation").addClass('d-none')
  });
  $(".form-btn").click(function(){
    alert('data sent!');
  });
  //details page load button
  $("#property").click(function(){
    alert('I have been clicked')
  });

  //page redirect no refresh
  $("#pageRedirect").click(function(){
    alert("clicked")
  });

  //load html file on button click
  $("#vacancies").click(function(){
    $("#update").load("/admin/dashboard/vacancies/");
    //alert('Done loading content');
  });
  $("#update-content").click(function(){
    $("#update").load("/admin/dashboard/bookings/");
  });

  $("#pending").click(function(){
    $("#update").load("/admin/dashboard/pending-leave-request/");
  });
  $("#leaves").click(function(){
    $("#update").load("/admin/dashboard/approved-leaves/");
  });
  $("#statistics").click(function(){
    $("#update").load("/admin/dashboard/sales/statistics/");
  });
  //accept request to leave
  $('#approve').click(function () {
    alert('I am working.');
  });
  //ajax delet action
  $('.delete').on('click', function(e){
    e.preventDefault()
    const url = $(this).attr('href');
    $.ajax({
      url: url,
      type: 'DELETE',
      beforesend: function(xhr){
        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoekn"));
      },
      success: function(data){
        alert(data.message);
      },
      error: function(xhr, textStatus, errorThrown){
        alert('Error' + xhr.responseJSON.error);
      }
    });
  });
});