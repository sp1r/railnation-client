$(document).on('ready',function(){

    if(getCookie('n') && getCookie('p')){
        $('.login-form [name=username]').val(getCookie('n'));
        $('.login-form [name=password]').val(getCookie('p'))
    }

    $.ajax({
        url: 'api/v1/login/status',
        type: 'GET',
        contentType: "application/json",
        success: function (data) {
            if(data.code === 0){
                if(data.data.logged_in){
                    initWorld();
                }
            }
        },
        error: function () {
            console.log('error login status');
        }
    });

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
                            load.removeClass('active');
                        }
                    });
                }else{
                    console.log('error');
                    load.removeClass('active');
                }
            },
            error: function (data) {
                console.log(data);
            }
        });


    });

    $('.world-menu .sign-out').on('click', function(e){
        e.preventDefault();
        $('.world-box').removeClass('active');
    });

    $(document).on('click', '.world-row', function(e){
        e.preventDefault();
        var worldID = $(this).attr('data-id'),
            load = $('.worlds-list-box .load-box');

        load.addClass('active');
        console.log('world - ' + worldID);

        joinWorld(worldID, load);

    });

    $(document).on('click', '.toggle-autocollect', function(e){
        e.preventDefault();

        var status = 'enable',
            selector = 'fa-toggle-on',
            self = $(this);

        if( self.hasClass('fa-toggle-on') ){
            status = 'disable';
            selector = 'fa-toggle-off';
        }

        console.log(status, selector);

        $.ajax({
            url: 'api/v1/autocollect/'+ status,
            type: 'POST',
            contentType: "application/json",
            success: function (data) {
                self.removeClass('fa-toggle-on fa-toggle-off');

                if(data.code === 0){
                    self.addClass(selector);
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





    function initWorld() {
        $('.world-box').addClass('active');
        loadAutocollect();
        loadStation();
        loadResources();
        updateData();
    }

    function updateData(){
        setInterval(function(){
            loadResources();
            loadCollectStats();
        },60000);
    }

    function joinWorld(id, load) {
        $.ajax({
            url: '/api/v1/join/'+id,
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    initWorld();
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
    }

    function loadAutocollect() {
        $.ajax({
            url: 'api/v1/autocollect/',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    var html = '<div class="title">Коллектор бонусов',
                        selector = 'on';

                    if(!data.data){
                        selector = 'off';
                    }
                    html += '<i class="toggle-autocollect fa fa-toggle-'+selector+'"></i></div>';

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

                        var html = '<div class="table">';
                        $.each(data.data,function(n, val){
                            var name = '';
                            if(n == "collected"){name = 'Собрано'}
                            else if(n == "errors"){name = 'Ошибок'}
                            else if(n == "tickets"){ name = 'Билетов'}

                            html += '<div class="table-row '+ n +'">';
                            html += '<div>' + name + '</div>';
                            html += '<div class="value">' + val + '</div>';
                            html += '</div>';
                        });
                        html += '</div>';

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

    function loadStation() {
        $.ajax({
            url: '/api/v1/station/',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    var html = '';

                    html += '<div class="title">Станция</div>';
                    html += '<div class="table">';
                    $.each(data.data, function(i, build){
                        html += '<div class="build-row table-row">';
                        html += '<div class="build-name">' + build.name + '</div>';
                        html += '<div class="build-lvl">' + build.level + '</div>';

                        if(build.build_in_progress){
                            html += '<div class="build-progress">' + build.build_finish_at + '</div>';
                        }else{
                            html += '<div class="build-progress"></div>';
                        }

                        if(build.video_watched){
                            html += '<div class="build-video-watched"><i class="fa fa-video-camera"></i></div>';
                        }else{
                            html += '<div class="build-video-watched"></div>';
                        }

                        html += '<div class="clear"></div>';
                        html += '</div>';
                    });
                    html += '</div>';

                    $('.station-box').html(html);

                }else{
                    alert(data.message);
                }
            },
            error: function (data) {
                alert('error station');
                console.log(data);
            }
        });
    }

    function loadResources() {
        $.ajax({
            url: 'api/v1/resources',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    var amount = data.data.amount;

                    $('.resources-box .money .value').text(numberWithCommas(amount[0]));
                    $('.resources-box .gold .value').text(numberWithCommas(amount[1]));
                    $('.resources-box .prestige .value').text(numberWithCommas(amount[2]));
                }else{
                    alert(data.message);
                }
            },
            error: function (data) {
                alert('error resources');
                console.log(data);
            }
        });
    }

    function loadCollectStats() {
        $.ajax({
            url: 'api/v1/autocollect/stats',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    if(data.data){
                        var box = $('.autocollect-statistic-box');

                        $.each(data.data,function(n, val){
                            box.find('.'+n+ ' .value').text(val);
                        });
                    }
                }
            },
            error: function (data) {
                alert('error autocollect stats');
                console.log(data);
            }
        });
    }

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

    function numberWithCommas(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }



});
