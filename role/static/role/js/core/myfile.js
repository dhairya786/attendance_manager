
console.log("cool");

$(function(){

    $(".dropdown-menu .ok").click(function(){
      $("#one").text($(this).text());
   });

});


$(function(){

    $(".dropdown-menu .good").click(function(){
      $("#dr").text($(this).text());
   });

});