//===============================================================================//
//===отправка и получение формы js, потом будет склеин с основным файлом по js===//
//===============================================================================//

if (window.jQuery) {
  console.log("Jquery подключен!");
}

$( document ).ready(function() {
    sendFormToServer();
});

function sendFormToServer(){ //основная форма
    var $mark = $("#mark"),
        $orthoErrors = $("#orthoErrors"),
        $punctErrors = $("#punctErrors"),
        $nextTime = $(".nextTime"),
        $originalText = $("#originalText"),
        $blockRules = $("#blockRules"),
        $nextDataTime = $(".nextDataTime"),
       /* $classKey = $(".key"),*/
        $idKey = $("#key"),
        
        allErrors = [], //хранилище всех ошибок
        numberOfErrors = 0, //порядковый номер ошибки для индефикации по id
        allText = ""; //хранилище воссозданного оригинального текста для вставки в html
    
    $("#yes").click(function(){ //вызываем событие submit при нажатии кнопки
        $('#dictionForm').submit();
        $('.dictation').hide();
        $('.preload').removeClass('hide');
        console.log( $("#dictionForm").serialize() );
    });
    
    $('#dictionForm').submit(function(event){ //обрабатываем событие submit 
        event.preventDefault();
        
        $.getJSON("/zhivoeslovo/ajax/results/", $("#dictionForm").serialize(), function(data){
            console.log("Ответ с сервера пришел:");
            console.log(data);
            //data.grade = 5;
            
            if (data.grade == 5) { //проверка приходящей оценки за диктант
                /*$classKey.text(data.confirmation);*/
                $idKey.val(data.confirmation);
                
                $(".preload").addClass("hide");
                $('.dictation').addClass("hide");
                $(".exellent").removeClass("hide");
                $(".mersy").removeClass("hide");
            } else if(data.grade < 3){
                $(".preload").addClass("hide");
                $('.dictation').addClass("hide");
                $(".sm").removeClass("hide");
                $(".mersy").removeClass("hide");
            } else {
                // console.log(data.markup);
                
                //Расфасовка информации с сервера =====start======
                // перебираю весь объект murkup который содержит все слова от присланного диктанта и ошибки внутри
                for(var i in data.markup){
                    if(data.markup[i].length > 0){ //если в слове есть ошибка(и)
                        allErrors.push( data.markup[i] );
                        var spanError = ' <span id = "error' + numberOfErrors +'" class = "errorInWord">'+ i +'</span> ';
                        allText += spanError;
                        numberOfErrors++;
                    } else { //если в слове нет ошибок
                        allText += i;
                    }
                }
                //Расфасовка информации с сервера =====the end======
                console.dir(allErrors);
                
                //создание id="blockRules" ====start====
                //создаем теги для html содержащие информацию об ошибках, для (div id="blockRules")
                //Правильный ответ и правило написания
                for(i = 0; i < allErrors.length; i++) {
                    var htmlData = '<div id ="setOfRules' + i + '" class = "setOfRules">';
                    for( var b in allErrors[i]){
                        htmlData += '<p class = "right_spelling green">' + allErrors[i][b].right_answer + '</p>';
                        htmlData += '<p class = "rulez addtext">' + allErrors[i][b].comment + '</p>';
                        //allErrors[i][b].comment
                        //allErrors[i][b].right_answer
                        //allErrors[i][b].type
                    }
                    htmlData+= "</div>";
                    $blockRules.append(htmlData);
                }
                //создание id="blockRules" ====the end====
                
                //console.log(allText);
                $mark.append(" " + data.grade); //указываю оценку в html
                $orthoErrors.text(data.ortho_errors); //указываю число орфографических ошибок в html
                $punctErrors.text(data.punct_errors); //указываю число пунктуационных ошибок в html
                $originalText.text(""); //очистить содержание внутри тэга в #originalText
                $originalText.append(allText); //добавить восозданный оригинальный текст в html
                $(".setOfRules").css("display", "none");
                
                
                //click On Error ====start====
                //у каждой ошибки есть свой пакет с информацией о ней, пакеты лежат в дивах типа <div id ="setOfRules0">
                //при нажатии на нужную ошибку соответствующий блок получает параметры display: block;
                $(".errorInWord").click(function(event){
                    $(".setOfRules").css("display", "none");
                    var regExp = /\d+/;
                    var errorNumber = event.currentTarget.id.match(regExp)[0]; // из id  типа "error24" удалаем слово, и оставляем цифры в конце
                    $("#setOfRules" + errorNumber).css("display", "block");
                });
                //click On Error ====the end====
                $(".result").removeClass("hide");
                $('.dictation').addClass("hide");
                $(".preload").addClass("hide");
                $("#setOfRules0").css("display", "block");
            }
            
            $nextTime.text(data.next_time); //указываю время в часах следующего диктанта в html
        })
        .error(function(data) {
            console.log("Ошибка выполнения ajax"); 
            console.log(data); 
        });
    });
    
    $('#exellentDictionForm').submit(function(event){
        event.preventDefault();
    });
}
