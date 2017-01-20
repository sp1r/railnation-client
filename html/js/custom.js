$(document).on('ready',function(){

    $('.login-form').on('submit', function(e){
        e.preventDefault();
        var username = $('input[name=username]').val(),
            password = $('input[name=password]').val();

        $.ajax({
            url: 'api/v1/login',
            type: 'POST',
            contentType: "application/json",
            data: JSON.stringify({
                "username": username,
                "password": password
            }),
            success: function (data) {
                console.log(data);

                if(data.code === 0){
                    $.ajax({
                        url: 'api/v1/worlds',
                        type: 'GET',
                        contentType: "application/json",
                        success: function (d) {
                            if(d.code === 0){
                                if(d.data.length){
                                    var worlds = d.data;


                                    console.log(worlds);

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
