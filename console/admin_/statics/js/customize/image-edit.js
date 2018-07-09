define(['utils'], function (utils) {
    var param = utils.getUrlParams();
    var id = decodeURIComponent(param.id);
    var is_protect = false;
    var is_public = false;
    var format = "";
    var image_type = "";
    utils._ajax({
        url: '/admin/describe_images',
        contentType: 'application/json',
        data: JSON.stringify({
            action: 'DescribeImagesList',
            owner: $('#owner').val(),
            zone: $('#zone').val(),
            image_id: id
        }),
        finalCB: function (result) {
            var data = result.data[0];
            format = data.format;
            image_type = data.image_type;
            $("#name").val(data.name);
            $("#format").html(data.format);
            $("#image_type").html(data.image_type);
            $("#status").html(data.status);
            if(data.protected){
                $("#open_protect").addClass('active');
                is_protect = true;
            }else{
                $("#close_protect").addClass('active');
                is_protect = false;
            }
            if(data.public != 'private'){
                $("#open_public").addClass('active');
                is_public = true;
            }else{
                $("#close_public").addClass('active');
                is_public = false;
            }
        }
    });
    $(".switch_button").on('click', function () {
        $(this).parent().find('.switch_button').removeClass('active');
        $(this).addClass('active');
        if($(this).attr('name') == 'is_protect'){
            is_protect = $(this).attr('value');
        }
        if($(this).attr('name') == 'is_public'){
            is_public = $(this).attr('value');
        }
    });
    $("#edit").click(function(){
        var name = $("#name").val();
        if (name.trim() == "") {
            utils.errMsg("名称不能为空");
            return false;
        }
        var param = {
            image_id:id,
            name:name,
            zone:$("#zone").val(),
            owner:$("#owner").val(),
            disk_format:format,
            is_public:is_public,
            image_type:image_type,
            is_protect:is_protect,
        };
        utils._ajax({
            url: "/admin/UpdateImageFile",
            data: param,
            succCB: function () {
                utils.succMsg('镜像修改成功');
                location.href = '/admin/customize/images';
            },
            errCB: function (err) {
                utils.errMsg(err.ret_msg);
            },
            error: function () {
                utils.errMsg('镜像修改失败');
            }
        });
    });
});