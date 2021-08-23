$(function() {
    $('input#capture_button').on('click', function(e) {
        e.preventDefault()
        $.getJSON('/background_process',
            function(data) {
                console.log(data)

                // random positions not to display
                var to_hide = new Array(4), i=0;
                // while (i<4) {
                //     var x = Math.floor(Math.random() * 15);
                //     if (!to_hide.includes(x)){
                //         to_hide[i] = x
                //         i++;
                //     }
                // }
                // console.log(to_hide)
                
                // // shuffle results order
                // var index_arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14];
                // var shuffled = index_arr.sort((a, b) => 0.5 - Math.random());

                // images and scores
                var element = document.getElementById("char");
                for (let i=0; i<15; i++){
                    // var index = shuffled[i]
                    var img = document.createElement("img");
                    img.src = data.char_lst[i+1];
                    // var cap = document.createElement("figcaption");
                    // var score = document.createTextNode(data.scores[i]);
                    // cap.appendChild(score);
                    var rect = document.createElement("div");
                    rect.className = "rectangle";
                    var h = (parseFloat(data.scores[i+1])+9)**2/1.5+10
                    rect.style.setProperty("height", h.toString()+"px")
                    var fig = document.createElement("figure");
                    fig.appendChild(img);
                    fig.appendChild(rect);
                    element.appendChild(fig);

                    if (to_hide.includes(i)) {
                        fig.style.setProperty("visibility", "hidden")
                    }
                }	

                // script
                var p = document.getElementById("script");
                var text = document.createTextNode(data.msg);
                p.appendChild(text)

                // photo and top result
                var element = document.getElementById("bottomImage");

                var img = document.createElement("img");
                img.src = "static/shots/photo.jpg";
                img.style.setProperty("height", "350px");
                var fig = document.createElement("figure");
                fig.appendChild(img);
                element.appendChild(fig);

                var img = document.createElement("img");
                img.src = data.char_lst[0];
                img.style.setProperty("height", "350px");
                var fig = document.createElement("figure");
                fig.appendChild(img);
                element.appendChild(fig);
        });
        return false;
    });
    });