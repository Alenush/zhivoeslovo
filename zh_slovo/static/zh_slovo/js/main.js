$(document).ready(function(){
  var popupDefaults = {
    items: {
        src: '#check_send',
        type: 'inline'},
    removalDelay: 300,
    callbacks: {
      beforeOpen: function() {
      this.st.mainClass = this.st.el.attr('data-effect');
      }
    },
    mainClass: 'mfp-fade',
    idClick: true
  }
  
  Mywindow = $(window);
  widthWindow = window.innerWidth;
  var help =  $('.help');
 
  
  $('#open_pop').on("click", function(event){
    event.preventDefault()
    var custom_text_l = $("#custom_text").val()
    if(custom_text_l.length > 0 && custom_text_l!=" "){
      $(this).magnificPopup(popupDefaults).magnificPopup('open');
    }
    else{alert("Введите, пожалуйста, текст диктанта")}
  });
  
  // $('#pers_data_submit').on("click", function(){
  //   $('.exellent').hide();
  //   $(".preload").removeClass("hide");
  // });
  
  /*$('#custom_text')[0].addEventListener('paste',function(event){
    event.preventDefault()
  })*/
  
  
  
  $('.help_icon').on('click', function(){
    help.toggleClass('shrink')
    help.toggleClass('shrink_reverse')
  })
  
  Mywindow.resize(function(){
    InstCarusel.sizeImg = $('.instImg').width();
    InstCarusel.makeMeFirst();
  })
  /*инстаграмовские фоточки*/
  InstCarusel.sizeImg = $('.instImg').width();
  InstCarusel.carusel = $('#carusel');
  InstCarusel.lastImg = $('#lastImg');

  InstCarusel.leftButton = $('#careselControlLeft'); 
  InstCarusel.rightButton = $('#careselControlRight'); 

  InstCarusel.moveButton();
});
