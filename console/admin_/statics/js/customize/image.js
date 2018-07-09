define(['utils'], function (utils) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var select_image = {};
    var columns = [{
        "data": "name",
        "name": "name",
        "id": "id"
    }, {
        "data": "type",
        "name": "type"
    }, {
        "data": "status",
        "name": "status"
    }, {
        "data": "image_type",
        "name": "image_type"
    }, {
        "data": "size",
        "name": "size"
    }, {
        "data": "format",
        "name": "format"
    }, {
        "data": "protected",
        "name": "protected"
    }, {
        "data": "public",
        "name": "public"
    }];
    var columnDefs = [{
        targets: 0,
        render: function (data, r, c) {
            var str = data;
            var hidden = '<input value=' + c.id + ' type="hidden" />';
            return str + hidden;
        }
    }, {
        targets: 1,
        render: function (data) {
            var str = data == 'private_image' ? '用户制作' : '平台制作';
            return str;
        }
    }, {
        targets: 2,
        render: function (data) {
            var str = data == 'active' ? '可用' : '不可用';
            return str;
        }
    }, {
        targets: 4,
        render: function (data) {
            var str = data / (1024 * 1024);
            if ((str / 1024) > 1) {
                str = parseInt(str / 1024) + 'G';
            } else {
                str = parseInt(str) + 'M';
            }
            return str;
        }
    }, {
        targets: 6,
        render: function (data) {
            return (data ? '是' : '否');
        }
    }, {
        targets: 7,
        render: function (data) {
            return (data == 'public' ? '公开' : '不公开');
        }
    }];
    var _datatable = utils.datatable($("#images_list"), {
        columns: columns,
        columnDefs: columnDefs
    }, {url: '/admin/describe_images', data: {action: 'DescribeImagesList', owner: owner, zone: zone}});

    utils.tableClick($("#images_list"), {
        onCB: function (obj) {
            select_image = {
                id: obj.find('td').eq(0).find('input').val(),
                protected: (obj.find('td').eq(6).html() == '是'),
            };
            $("#edit_image").removeAttr('disabled');
            $("#delete_image").removeAttr('disabled');
        },
        offCB: function () {
            select_image = {};
            $("#edit_image").attr('disabled', 'disabled');
            $("#delete_image").attr('disabled', 'disabled');
        }
    });
    $("#edit_image").click(function () {
        location.href = $(this).data('href') + '?id=' + select_image.id;
    });
    $("#delete_image").click(function () {
        $('#delete_image_modal').modal();
    });
    utils.refreshDataTable(_datatable);
    $("#delete_image_btn").click(function () {
        if(select_image.protected){
            utils.errMsg("保护镜像无法删除，请重新选择");
            $('#delete_image_modal').modal('hide')
            return false;
        }
        utils._ajax({
            url: '/admin/DeleteImageFile',
            data: {
                action: 'delete_image',
                owner: $('#owner').val(),
                zone: $('#zone').val(),
                image_id: select_image.id
            },
            succCB: function (result) {
                utils.succMsg("删除成功");
                $('#delete_image_modal').modal('hide');
                _datatable.ajax.reload();
            },
            errCB: function (result) {
                utils.errMsg(result.ret_msg);
            }
        });
    });
});
