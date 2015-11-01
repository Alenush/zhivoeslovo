//===============================================================================//
//===отправка и получение формы js, потом будет склеин с основным файлом по js===//
//===============================================================================//

$( document ).ready(function() {
    inform();
    calendar();
    sendFormToServer();
});

function inform(){
    // console.log("id следующего диктанта: " + next_id );
    // console.log("дата следующего диктанта: " + next_date);
    // console.log("месяц следующего диктанта: " + next_month);
    // console.log("время следующего диктанта: " + next_time);
    // console.log("список всех диктантов: " + all_dict);
    
    //console.log( newAll_dict2 );
    
    var monthWord = ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"];
    next_month = monthWord[next_month -1];
}

function calendar(){

    var monthWord = ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"];
    var weekDayWord = ["понедельник","вторник","среда","четверг","пятница","суббота","воскресенье"];
    var newStorageOfDatesOfDictations = [];
    var newAlldict = $.parseJSON( all_dict );
    var numbersOfcalendar = "";
    
    // console.dir( newAlldict );
    
    for(var i = 0; i < newAlldict.length ;i++){ //преобразую данные с сервера в нормальный вид
        var temprory = {};
        temprory.dateNumber = newAlldict[i][0];
        temprory.dateMonth = monthWord[ newAlldict[i][1]-1 ];
        temprory.weekDay = weekDayWord[ newAlldict[i][2]-1 ];
        //temprory.year = newAlldict[i][3];
        temprory.time = newAlldict[i][3] + ":" +newAlldict[i][4];
        temprory.dictationId = newAlldict[i][5];
        
        newStorageOfDatesOfDictations.push( temprory );
    }
    
    for(var i = 0; i < newStorageOfDatesOfDictations.length; i++){ //сформеровать календарь из упорядоченных данных с сервера
        numbersOfcalendar += '<div class ="col-md-3 col-xs-4 center"><p class ="date">' + newStorageOfDatesOfDictations[i].dateNumber + '</p>';
        numbersOfcalendar += '<p>'+ newStorageOfDatesOfDictations[i].dateMonth +'</p>';
        numbersOfcalendar += '<p>'+ newStorageOfDatesOfDictations[i].weekDay +'</p>';
        numbersOfcalendar += '<p>'+ newStorageOfDatesOfDictations[i].time +'</p></div>';
    }
    $(".calendar").append( numbersOfcalendar ); //вставить сформерованные даты диктантов в календарь
    
    for(var i = 0; i < newStorageOfDatesOfDictations.length; i++){ //пройтись по датам в календаре и добавить им уникальный idномер диктанта
        $(".calendar").find("div")[i].id = "DictationCalendarId" + newStorageOfDatesOfDictations[i].dictationId;
    }
    $(".calendar").find("#DictationCalendarId" + next_id).addClass("red"); //добавить красный цвет в календаре след. диктанту
}

function sendFormToServer(){ //основная форма ajax отправки данных
    
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
    });
    
    $('#dictionForm').submit(function(event){ //обрабатываем событие submit
        event.preventDefault();
        
        $.getJSON("/zhivoeslovo/ajax/results/", $("#dictionForm").serialize(), function(data){
            // console.log("Ответ с сервера пришел:");
            // console.log(data);
            //data.grade = 5;
            
            if (data.grade == 5) { //проверка приходящей оценки за диктант
                /*$classKey.text(data.confirmation);*/
                
                $(".preload").addClass("hide");
                $('.dictation').addClass("hide");
                $(".exellent").removeClass("hide");
                $(".mersy").removeClass("hide");
                
                $idKey.val(data.confirmation);

            } else if(data.grade < 3){
                
                $(".preload").addClass("hide");
                $('.dictation').addClass("hide");
                $(".sm").removeClass("hide");
                $(".mersy").removeClass("hide");
                
            } else {
                //Расфасовка информации с сервера =====start======
                //Перебираю весь объект murkup который содержит все слова от присланного диктанта и ошибки внутри
                for(var i = 0; i < data.markup.length; i ++){
                    if(data.markup[i].errors.length > 0){
                        allErrors.push( data.markup[i] );
                        if( data.markup[i].errors.length < 2){
                            if ( data.markup[i].errors[0].type == "PU" ) {
                                var spanError = '<span id = "error' + numberOfErrors +'" class = "PU errorsInOriginText">'+ data.markup[i].text +'</span>';
                            } else {
                                var spanError = '<span id = "error' + numberOfErrors +'" class = "OR errorsInOriginText">'+ data.markup[i].text +'</span>';
                            }
                        } else {
                            var spanError = '<span id = "error' + numberOfErrors +'" class = "OR errorsInOriginText">'+ data.markup[i].text +'</span>';
                        }
                        allText += spanError;
                        numberOfErrors++;
                    } else {
                        allText += data.markup[i].text;
                    }
                }
                //Расфасовка информации с сервера =====the end======
                // console.dir(allErrors);
                
                //создание id="blockRules" ====start====
                //создаем теги для html содержащие информацию об ошибках, для (div id="blockRules")
                //Правильный ответ и правило написания
                for(i = 0; i < allErrors.length; i++) {
                    var htmlData = '<div id ="setOfRules' + i + '" class = "setOfRules">';
                    var rightHas = false
                    if ( allErrors[i].errors.length > 1 ) {
                        for(var c = 0; c < allErrors[i].errors.length; c++){
                            if(rightHas == false){
                                htmlData += '<p class = "right_spelling green">' + allErrors[i].errors[c].right_answer + '</p>';
                                rightHas = true;
                            }
                            htmlData += '<p class = "rulez addtext">' + allErrors[i].errors[c].comment + '</p>';
                        }
                    } else {
                        for(var c = 0; c < allErrors[i].errors.length ;c++){
                            htmlData += '<p class = "right_spelling green">' + allErrors[i].errors[c].right_answer + '</p>';
                            htmlData += '<p class = "rulez addtext">' + allErrors[i].errors[c].comment + '</p>';
                            //allErrors[i].errors[c].comment
                            //allErrors[i].errors[c].right_answer
                            //allErrors[i].errors[c].type
                        }
                        
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
                $(".mersy").removeClass("hide");
                
                
                //click On Error ====start====
                //у каждой ошибки есть свой пакет с информацией о ней, пакеты лежат в дивах типа <div id ="setOfRules0">
                //при нажатии на нужную ошибку соответствующий блок получает параметры display: block;
                $(".errorsInOriginText").click(function(event){
                    $(".setOfRules").css("display", "none");
                    var regExp = /\d+/;
                    var errorNumber = event.currentTarget.id.match(regExp)[0]; // из id  типа "error24" удалаем слово, и оставляем цифры в конце
                    $("#setOfRules" + errorNumber).css("display", "block");
                });
                //click On Error ====the end====
                $(".result").removeClass("hide");
                $("#instGallery").removeClass("hide");
                $('.dictation').addClass("hide");
                $(".preload").addClass("hide");
                $("#setOfRules0").css("display", "block");
            }
            
            $nextTime.text(next_time); //указываю время в часах следующего диктанта в html на всех страницах
            $nextDataTime.text(next_date + " " + next_month);
        })
        .error(function(data) {
            console.log("Ошибка выполнения ajax");
        });
    });
    
    $('#exellentDictionForm').submit(function(event){ //отосладть данные об отличнике через ajax
        event.preventDefault();
        $.getJSON("/zhivoeslovo/ajax/send_results/", $("#exellentDictionForm").serialize(), function(data){
            console.log(data);
            $(".preload").addClass("hide");
        })
        .error(function(data) {
            console.log("Ошибка выполнения ajax"); 
        });
    });
}
