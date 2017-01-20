$(document).on('ready',function(){

    $('.login-form').on('submit', function(e){
        e.preventDefault();
        var username = $('input[name=username]').val(),
            password = $('input[name=password]').val(),
            submit = $('button[type=submit]'),
            load = $('.load-box'),
            worldsBox = $('.worlds-box');

        if(username && password){
            load.addClass('active');
        }

        $.ajax({
            url: 'api/v1/login',
            type: 'POST',
            contentType: "application/json",
            data: JSON.stringify({
                "username": username,
                "password": password
            }),
            success: function (data) {
                if(data.code === 0){
                    $.ajax({
                        url: 'api/v1/worlds',
                        type: 'GET',
                        contentType: "application/json",
                        success: function (d) {
                            if(d.code === 0){
                                if(d.data.length){
                                    var worlds = '';

                                    $.each(d.data, function(world){
                                        worlds += '<div class="world-row">';
                                        worlds += '<div class="worldId">world.worldId</div>';
                                        worlds += '<div class="worldName">world.worldName</div>';
                                        worlds += '<div class="era">world.era</div>';
                                        worlds += '<div class="eraDay">world.eraDay</div>';
                                        worlds += '</div>';
                                    });

                                    worldsBox.html(worlds).addClass('active');
                                    load.removeClass('active');
                                }
                            }
                        },
                        error: function (data) {
                            console.log(data);
                        }
                    });
                }else{
                    console.log('error');
                }
            }
        });


    });

});
