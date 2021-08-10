$(function() {
    $('input#capture_button').on('click', function(e) {
        e.preventDefault()
        $.getJSON('/background_process',
            function(data) {
                console.log(data)

                var p = document.getElementById("script");
                var text = document.createTextNode(data.msg);
                p.appendChild(text)

                var element = document.getElementById("char");
                for (let i=0; i<data.char_lst.length; i++){
                    var img = document.createElement("img");
                    img.src = data.char_lst[i];
                    var cap = document.createElement("figcaption");
                    var score = document.createTextNode(data.scores[i]);
                    cap.appendChild(score);
                    var fig = document.createElement("figure");
                    fig.appendChild(img);
                    fig.appendChild(cap);
                    element.appendChild(fig);
                }	
        });
        return false;
    });
    });