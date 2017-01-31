$(document).on('ready',function(){

    if(getCookie('n') && getCookie('p')){
        $('.login-form [name=username]').val(getCookie('n'));
        $('.login-form [name=password]').val(getCookie('p'))
    }

    $('.login-form').on('submit', function(e){
        e.preventDefault();
        var username = $('input[name=username]').val(),
            password = $('input[name=password]').val(),
            save = $('input[name=save]').val(),
            submit = $('button[type=submit]'),
            load =  $(this).find('.load-box');

        if(save && username && password){
            createCookie('n', username);
            createCookie('p', password);
        }

        return false;

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

                                    $.each(d.data, function(i, world){
                                        worlds += '<div class="world-row" data-id="' + world.worldId + '">';
                                        worlds += '<div class="worldName">' + world.worldName + '</div>';
                                        worlds += '<div class="era inline">Эпоха ' + world.era + '</div>';
                                        worlds += '<div class="eraDay inline">День ' + world.eraDay + '/14</div>';
                                        if(world.cityName){
                                            worlds += '<div class="eraDay inline">Город ' + world.cityName + '</div>';
                                        }
                                        worlds += '<div class="playersOnline inline">Онлайн ' + world.playersOnline + '</div>';
                                        worlds += '<div class="clear"></div>';
                                        worlds += '</div>';
                                    });

                                    $('.worlds-list').html(worlds);
                                    $('.worlds-list-box').addClass('active');
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
            },
            error: function (data) {
                console.log(data);
            }
        });


    });

    $('body').on('click', '.world-row', function(e){
        e.preventDefault();
        var worldID = $(this).attr('data-id'),
            load = $('.worlds-list-box .load-box');

        load.addClass('active');
        console.log('Click, world ID - ' + worldID);

        $.ajax({
            url: '/api/v1/join/'+worldID,
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    $('.world-box').addClass('active');
                    loadAutocollect();


                }else{
                    alert(data.message);
                }
                load.removeClass('active');
            },
            error: function (data) {
                alert('error join');
                console.log(data);
                load.removeClass('active');
            }
        });


    });

    $('.world-menu .station').on('click', function(e){
        e.preventDefault();

        $.ajax({
            url: '/api/v1/station/',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    var html = '<div class="station-box table">';
                    $.each(data.data, function(i, build){
                        html += '<div class="build-row table-row">';
                        html += '<div class="build-name">' + build.name + '</div>';
                        html += '<div class="build-lvl">' + build.level + '</div>';
                        if(build.build_in_progress){
                            html += '<div class="build-progress">' + build.build_finish_at + '</div>';
                        }
                        if(build.video_watched){
                            html += '<div class="build-video-watched"><i class="fa fa-video-camera"></i></div>';
                        }
                        html += '<div class="clear"></div>';
                        html += '</div>';
                    });

                    console.log('click');

                    $('.center-box').html(html);

                }else{
                    alert(data.message);
                }
            },
            error: function (data) {
                alert('error station');
                console.log(data);
            }
        });
    });

    $('.autocollect-status-box .fa').on('click', function(e){
        e.preventDefault();

        var selector = $(this).attr('class'),
            status = 'enable';

        if(selector === 'fa fa-toggle-on'){
            status = 'disable';
            selector = 'fa fa-toggle-off';
        }else{
            selector = 'fa fa-toggle-on';
        }

        console.log(status, selector);

        $.ajax({
            url: '/api/v1/autocollect/'+ status,
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    $(this).attr(selector);
                }else{
                    alert(data.message);
                }
            },
            error: function (data) {
                alert('error autocollect status');
                console.log(data);
            }
        });
    });

    function createCookie(name, val) {
        if(val && name){
            var cookieLiveTime = 60 * 60 * 24 * 30 * 1000;
            var cookieDate = new Date(new Date().getTime() + cookieLiveTime);
            document.cookie = name +"="+ val +"; path=/; expires=" + cookieDate.toUTCString();
        }
    }

    function getCookie(name) {
        var matches = document.cookie.match(new RegExp(
            "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
        ));
        return matches ? decodeURIComponent(matches[1]) : undefined;
    }

    function loadAutocollect() {
        $.ajax({
            url: 'api/v1/autocollect/',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    var html = 'Коллектор бонусов <div class="autocollect-status">',
                        selector = 'on';

                    if(data.data){
                        html += 'Включен';
                    }else{
                        html += 'Выключен';
                        selector = 'off';
                    }
                    html += '</div><i class="fa fa-toggle-'+selector+'"></i>';

                    $('.autocollect-status-box').html(html).addClass(selector);
                }
            },
            error: function (data) {
                alert('error loadAutocollect');
                console.log(data);
            }
        });

        $.ajax({
            url: 'api/v1/autocollect/stats',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    if(data.data){

                        var html = '';
                        $.each(data.data,function(n, val){
                            var name = '';
                            if(n == "collected"){name = 'Собрано'}
                            else if(n == "errors"){name = 'Ошибок'}
                            else if(n == "tickets"){ name = 'Билетов'}

                            html += '<div class="table-row">';
                            html += '<div class='+ n +'>' + name + '</div>';
                            html += '<div class="value">' + val + '</div>';
                            html += '</div>';
                        });

                        $('.autocollect-statistic-box').html(html);
                    }
                }
                console.log(data.data);
            },
            error: function (data) {
                alert('error loadAutocollect');
                console.log(data);
            }
        });
    }


});
