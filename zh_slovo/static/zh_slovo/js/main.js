$(document).ready(function(){              
 
  $('#submit').magnificPopup({
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
  });
  $('#pers_data_submit').on("click", function(){
    $('.exellent').hide();
    $(".preload").removeClass("hide");
  });
  
  /*$('#custom_text')[0].addEventListener('paste',function(event){
    event.preventDefault()
  })*/
});
  




/*Hinge effect popup
$('a.hinge').magnificPopup({
  mainClass: 'mfp-with-fade',
  removalDelay: 1000, //delay removal by X to allow out-animation
  callbacks: {
    beforeClose: function() {
        this.content.addClass('hinge');
    }, 
    close: function() {
        this.content.removeClass('hinge'); 
    }
  },
  midClick: true
});*/