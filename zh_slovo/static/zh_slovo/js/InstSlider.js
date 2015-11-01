var InstCarusel = {
  currentImg: 0,
  moveButton: function(){
    InstCarusel.rightButton.on('click', function(){
      InstCarusel.condition('-');
    });
    InstCarusel.leftButton.on('click', function(){
      InstCarusel.condition('+');
    });
  },
  condition: function(direction){
    var offset = InstCarusel.lastImg.offset().left
    var imgStop = InstCarusel.lastImg.width()
    var parStop = offset + imgStop

    if (direction == '+' && InstCarusel.currentImg > 0 ){
      InstCarusel.moveImg(direction);
      InstCarusel.currentImg--;
    }
    if (direction == '-' && parStop > widthWindow){
      InstCarusel.moveImg(direction);
      InstCarusel.currentImg++;
    }
  },
  moveImg:function(direction){
    InstCarusel.rightButton.off();
    InstCarusel.leftButton.off();
    var action = {};
    var attr = 'left';
    var fullMoveSize = InstCarusel.sizeImg+10
    action[attr] = ''+direction+'='+fullMoveSize+'px';
    InstCarusel.carusel.animate(action,1000,function(){
      InstCarusel.moveButton();
    })
  },
  makeMeFirst:function(){
    if(InstCarusel.currentImg>0){
      var position = '-'+(InstCarusel.sizeImg+10)*InstCarusel.currentImg+'px'
    }
    else{
      var position = 'auto'
    }
      InstCarusel.carusel.css('left',position)
  }
};