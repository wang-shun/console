define(['utils'], function (utils) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var name = '';
    var selected_source = {};
    var status = {
        'Normal' : '正常',
        'Modifying' : '修改中',
        'Recovering': '恢复中',
        'Creating' : '创建中',
        'Abnormal' : '异常',
    };
    var columns = [{
        "data": "name",
        "name": "name"
    }, {
        "data": "status",
        "name": "status"
    }, {
        "data": "type",
        "name": "type"
    }, {
        "data": "dev_num",
        "name": "dev_num"
    }, {
        "data": "disk_count",
        "name": "disk_count"
    }, {
        "data": "size",
        "name": "size"
    }, {
        "data": "used",
        "name": "used"
    }];
    var columnDefs = [{
        targets: 0,
        render: function (data, type, item) {
            return '<a href="/admin/sourceManage/memorySourceDetails?name=' + item.name + '">' + data + '</a>';
        }
    }, {
        targets: 1,
        render: function (data, type, item) {
            return status[data] || '异常';
        }
    },  {
        targets: 5,
        render: function (data, type, item) {
            return utils.toMemory(data,'KB','GB');
        }
    }, {
        targets: 6,
        render: function (data) {
            return utils.toMemory(data,'KB','GB');
        }
    }];
    var _datatable = utils.datatable($("#pools_memory_list"), {
        columns: columns,
        columnDefs: columnDefs
    }, {url: '/admin/pools/storage_resource/info', data: {owner: owner, zone: zone}});
    utils.tableClick($("#pools_memory_list"), {
        onCB: function (obj) {
            $("#edit_memory").removeAttr('disabled');
            $("#delete_memory").removeAttr('disabled');
            name = utils.selected_column(_datatable,0).find('a').html();
        },
        offCB: function () {
            $("#edit_memory").attr('disabled', 'disabled');
            $("#delete_memory").attr('disabled', 'disabled');
            name = "";
        }
    });
    $("#delete_memory").click(function(){
        var used = utils.selected_column(_datatable,4);
        var usedNum = used.html()
        if(usedNum != 0){
            $("#modal_center").html('['+name+']资源池下存在硬盘，无法直接删除.');
            $("#delete_memory_btn").hide();
        }else{
            $("#modal_center").html('确定删除存储池['+name+']？');
            $("#delete_memory_btn").show();
        }
        $("#delete_memory_modal").modal();
    });
    $("#edit_memory").click(function () {
        if (name) {
            location.href = $(this).data('href') + '?name=' + name;
        }
    });
    $("#delete_memory_btn").click(function(){
        utils._ajax({
            url: '/admin/pools/storage_resource/delete',
            contentType: 'application/json',
            data: JSON.stringify({
                owner: owner,
                zone: zone,
                name: name
            }),
            succCB: function (reault) {
                if(reault.ret_set.reault){
                    utils.succMsg('存储池池删除成功');
                }else{
                    utils.errMsg('存储池删除失败');
                }
            },
            errCB: function (err) {
                utils.errMsg(err.ret_msg);
            },
            error: function () {
                utils.errMsg('存储池删除失败');
            }
        });
        $('#delete_memory_modal').modal('hide');
        location.href = '/admin/sourceManage/memorySource';
    });
});