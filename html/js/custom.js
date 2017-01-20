$(document).on('ready',function(){

    $('.login-form').on('submit', function(e){
        e.preventDefault();

        console.log($(e.target).serialize());
        return;

        $.ajax({
            url: "",
            type: "POST",
            data: this.serialize(),
            success: function (d) {
                console.log('success', d);
            },
            error: function (d) {
                console.log('error', d);
            }
        });
    });

});
