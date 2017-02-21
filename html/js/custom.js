var translate = {
    Engine_house: {
        text: 'Депо',
        id: 0
    },
    Station: {
        text: 'Вокзал',
        id: 1
    },
    Maintenance_Hall: {
        text: 'Рельсовый завод',
        id: 2
    },
    Construction_yard: {
        text: 'Стройплощадка',
        id: 3
    },
    Bank: {
        text: 'Банк',
        id: 4
    },
    Licence: {
        text: 'Отдел лицензий',
        id: 5
    },
    Labor: {
        text: 'Лаба',
        id: 6
    },
    Hotel: {
        text: 'Отель',
        id: 7
    },
    Restaurant: {
        text: 'Ресторан',
        id: 8
    },
    Mall: {
        text: 'Рынчик',
        id: 9
    }
};



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
    loadTechnologies();

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
                alert('Ошибка входа, смотреть консоль');
                load.removeClass('active');
            }
        });


    });

    $('.world-menu .sign-out').on('click', function(){
        $('.world-box').removeClass('active');
    });

    $('.world-menu .fa').on('click', function(){
        var tab = $(this).data('tab');

        if(tab){
            $(this).addClass('active').siblings().removeClass('active');
            $('.'+tab +'-box').addClass('active').siblings().removeClass('active');
        }
    });

    $(document).on('click', '.tab-button', function(){
        if(!$(this).hasClass('active')){
            var index = $(this).attr('data-index'),
                body = $(this).closest('.tabs-box').find('.tab-content-box[data-index='+ index +']');

            $(this).siblings().removeClass('active');
            $(this).addClass('active');
            body.siblings().removeClass('active');
            body.addClass('active');
        }

    });

    $(document).on('click', '.build-droid-add', function(){
        var id = $('.build-droid-select').val(),
            name = $('.build-droid-select option:selected').text(),
            list = $('.build-droid-list');

        $.ajax({
            url: 'api/v1/build/'+ id,
            type: 'POST',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    var html = '<div class="build" data-id="'+id+'">';
                    html += '<span class="build-name">'+ name +'</span>';
                    html += '</div>';

                    list.append(html);
                }else{
                    console.log(data.message);
                }
            },
            error: function (data) {
                console.log('error add build');
                console.log(data);
            }
        });
    });

    $(document).on('click', '.build-droid-remove-all', function(){
        $.ajax({
            url: 'api/v1/buildqueue/clear',
            type: 'POST',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    $('.build-droid-list').text('');
                }else{
                    console.log(data.message);
                }
            },
            error: function (data) {
                console.log('error buildqueue clear');
                console.log(data);
            }
        });
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
                    console.log(data.message);
                }
            },
            error: function (data) {
                console.log('error autocollect status');
                console.log(data);
            }
        });
    });

    $(document).on('click', '.show-tickets-history', function(){
        $('.tickets-history-box').addClass('active');
    });

    $(document).on('click', '.show-watch_rewards-history', function(){
        $('.video-rewards-history-box').addClass('active');
    });

    $(document).on('click', '.popup-close', function(){
        $(this).closest('.popup-box').removeClass('active');
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
            loadStation();
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
                    console.log(data.message);
                }
                load.removeClass('active');
            },
            error: function (data) {
                console.log('error join');
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
                console.log('error loadAutocollect');
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
                            else if(n == "watch_rewards"){ name = 'Бонусы с просмотров'}
                            else if(n == "watched"){ name = 'Просмотрено видео'}

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
                console.log('error loadAutocollect');
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
                    var html = '',
                        i = 0;

                    html += '<div class="tab-buttons-box">';
                    html += '<span class="tab-button active" data-index="0">Станция</span>';
                    html += '<span class="tab-button" data-index="1">Билд дроид</span>';
                    html += '</div>';

                    html += '<div class="tab-content-box active" data-index="0">';
                    html += '<div class="table">';
                    $.each(data.data, function(i, build){
                        var name = build.name,
                            video = '';
                            nextLvl = build.level+1;

                        if(translate[build.name.replace(' ','_')]){
                            name = translate[build.name.replace(' ','_')].text;
                        }

                        html += '<div class="build-row table-row">';
                        html += '<div class="build-name">' + name + '</div>';

                        if(build.build_in_progress){
                            html += '<div class="build-lvl">' + build.level + '>'+ nextLvl +'</div>';
                            html += '<div class="build-progress"><i class="fa fa-wrench"></i><span class="build-finish-at">'+ unixDateToDateLeft(build.build_finish_at) +'</span></div>';
                        }else{
                            html += '<div class="build-lvl">' + build.level + '</div>';
                            html += '<div class="build-progress"></div>';
                        }

                        if(!build.video_watched){
                            if(build.name === 'Hotel' ||build.name === 'Hotel' ||build.name === 'Hotel' ){
                                video = '<i class="fa fa-video-camera"></i>';
                            }
                        }
                        html += '<div class="build-video-watched">'+ video +'</div>';

                        //html += '<div class="clear"></div>';
                        html += '</div>';
                    });
                    html += '</div>';
                    html += '</div>';

                    html += '<div class="tab-content-box build-droid-box" data-index="1">';

                    html += '<select class="build-droid-select">';
                    $.each(translate, function(name, val){
                        html += '<option value='+ i +'>'+ val.text +'</option>';
                        i++;
                    });
                    html += '</select>';
                    html += '<span class="build-droid-add"><i class="fa fa-plus"></i></span>';
                    html += '<span class="build-droid-remove-all"><i class="fa fa fa-times"></i></span>';
                    html += '<div class="build-droid-list"></div>';

                    html += '</div>';

                    $('.station-box').html(html);

                    $.ajax({
                        url: '/api/v1/buildqueue',
                        type: 'GET',
                        contentType: "application/json",
                        success: function (data) {
                            if(data.code === 0){
                                var html = '';

                                $.each(data.data, function(i, id){
                                    var name = '';
                                    $.each(translate, function(x, build){
                                        if(id === build.id){
                                            name = build.text;
                                        }
                                    });

                                    html += '<div class="build" data-id="'+id+'">';
                                    html += '<span class="build-name">'+ name +'</span>';
                                    html += '</div>';
                                });

                                $('.station-box .build-droid-list').html(html);
                            }else{
                                console.log(data.message);
                            }
                        },
                        error: function (data) {
                            console.log('error buildqueue');
                            console.log(data);
                        }
                    });

                }else{
                    console.log(data.message);
                }
            },
            error: function (data) {
                console.log('error station');
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
                    console.log(data.message);
                }
            },
            error: function (data) {
                console.log('error resources');
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
                            if(n === 'tickets' && val > 0 || n === 'watch_rewards' && val > 0){
                                box.find('.'+n+ ' .value').append('<i class="fa fa-gift show-'+ n +'-history"></i>');
                                loadTicketHistory();
                                loadVideoRewardsHistory();
                            }
                        });
                    }
                }
            },
            error: function (data) {
                console.log('error autocollect stats');
                console.log(data);
            }
        });
    }

    function loadTicketHistory() {
        $.ajax({
            url: 'api/v1/ticket/history',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data){
                    var html = '<div class="table">';
                    $.each(data, function(n, val){
                        html += '<div class="table-row"><span class="date">'+ unixDateToDate(val.date) +'</span><span class="reward">'+ val.reward +'</span></div>'
                    });
                    html += '<i class="fa fa-close popup-close"></i>';
                    html += '</div>';

                    $('.tickets-history-box').html(html);
                }
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    function loadTechnologies() {
        $.ajax({
            url: 'api/v1/technologies',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data.code === 0){
                    if(data.data){
                        createTabs('.research-box.active', 6, 1);
                        for(var i = 1; i <= 6; i++){
                            var html = '<div class="table">';
                            html += '<div class="table-row">';
                            html += '<span class="name"></span>';
                            html += '<span class="speed">Поинты</span>';
                            html += '<span class="speed">Цена</span>';
                            html += '<span class="speed">Вагонов</span>';
                            html += '<span class="speed">Скорость</span>';
                            html += '<span class="speed">Ускорение</span>';
                            html += '<span class="speed">Жизни</span>';
                            html += '</div>';

                            $.each(data.data, function(n, val){
                                if(i === val.era){
                                    if(val.speed){
                                        var upWaggons = '',
                                            upAcceleration = '',
                                            upEndurance = '',
                                            upSpeed = '';

                                        if(val.upgrades){
                                            $.each(val.upgrades, function(g, update){
                                                console.log(update);
                                                switch (update.type) {
                                                    case 'waggons':
                                                        upWaggons += '<span class="update" data-id="'+ g +'">+'+ update.effect +'</span>';
                                                        break;
                                                    case 'acceleration':
                                                        upAcceleration += '<span class="update"  data-id="'+ g +'">+'+ update.effect +'</span>';
                                                        break;
                                                    case 'speed':
                                                        upSpeed += '<span class="update" data-id="'+ g +'">+'+ update.effect +'</span>';
                                                        break;
                                                    case 'endurance':
                                                        upEndurance += '<span class="update" data-id="'+ g +'">+'+ update.effect +'</span>';
                                                        break;
                                                }
                                            });
                                        }

                                        html += '<div class="table-row research" data-id="'+ n +'">';
                                        html += '<span class="name">'+ val.name +'</span>';
                                        html += '<span class="research_cost"><span class="value">'+ val.research_cost +'</span></span>';
                                        html += '<span class="price"><span class="value">'+ val.price / 1000 + ' к' +'</span></span>';
                                        html += '<span class="waggons"><span class="value">'+ val.waggons + '</span>' + upWaggons + '</span>';
                                        html += '<span class="speed"><span class="value">'+ val.speed + '</span>' + upSpeed +'</span>';
                                        html += '<span class="acceleration"><span class="value">'+ val.acceleration + '</span>' + upAcceleration + '</span>';
                                        html += '<span class="endurance"><span class="value">'+ val.endurance + '</span>' + upEndurance + '</span>';
                                        html += '</div>';
                                    }else{
                                        if(val.name.indexOf('соединение') !== -1){
                                            val.name = 'Сцепка';
                                        }

                                        html += '<div class="table-row">';
                                        html += '<span class="name">'+ val.name +'</span>';
                                        html += '<span class="research_cost"><span class="value">'+ val.research_cost +'</span></span>';
                                        html += '<span></span>';
                                        html += '<span></span>';
                                        html += '<span></span>';
                                        html += '<span></span>';
                                        html += '<span></span>';
                                        html += '</div>';
                                    }
                                }
                            });

                            html += '</div>';
                            $('.research-box.active .tab-content-box[data-index='+ i +']').append(html);
                        }
                    }
                }
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    function loadTechnologiePoints() {
        $.ajax({
            url: 'api/v1/technologies/points',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data){
                    console.log(data);
                }
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    function loadVideoRewardsHistory() {
        $.ajax({
            url: 'api/v1/autowatch/rewards',
            type: 'GET',
            contentType: "application/json",
            success: function (data) {
                if(data){
                    var html = '<div class="table">';
                    $.each(data, function(n, val){
                        html += '<div class="table-row"><span class="date">'+ unixDateToDate(val.date) +'</span><span class="-reward">'+ val.reward +'</span></div>'
                    });
                    html += '<i class="fa fa-close popup-close"></i>';
                    html += '</div>';

                    $('.video-rewards-history-box').html(html);
                }
            },
            error: function (data) {
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

    function unixDateToDateLeft(time) {
        var seconds = parseInt(time - Date.now()/1000),
            date = new Date(1970,0,1);
        date.setSeconds(seconds);
        return date.toTimeString().replace(/.*(\d{2}:\d{2}:\d{2}).*/, "$1").substring(0,5);
    }

    function unixDateToDate(time) {
        return dateFormat(new Date(time*1000), 'dd.mm.yyyy - HH:MM');
    }

    function createTabs(cl, n, active){
        var html = '<div class="tabs-box">',
            buttonHtml = '<div class="tab-buttons-box">',
            contentHtml = '';

        for(var i = 1; i <= n; i++){
            var buttonCl = 'tab-button',
                contentCl = 'tab-content-box';

            if(active != undefined){
                if(i === active){
                    buttonCl += ' active';
                    contentCl += ' active';
                }
            }

            buttonHtml += '<div class="'+ buttonCl +'" data-index="'+ i +'">'+ i +'</div>';
            contentHtml += '<div class="'+ contentCl +'" data-index="'+ i +'"></div>';
        }
        buttonHtml += '</div>';

        html += buttonHtml;
        html += contentHtml;
        html += '</div>';

        $(cl).append(html);
    }
});
