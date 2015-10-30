$(document).ready(function(){ 
  $('#submit').on('click', function(event) {
    event.preventDefault();
      if($("#custom_text").val().length > 0 && $("#custom_text").val()!=" "){
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
      }
      else{alert("Введите, пожалуйста, текст диктанта")}
    })
    
  
  $('#pers_data_submit').on("click", function(){
    $('.exellent').hide();
    $(".preload").removeClass("hide");
  });
  
  /*$('#custom_text')[0].addEventListener('paste',function(event){
    event.preventDefault()
  })*/
});
  

