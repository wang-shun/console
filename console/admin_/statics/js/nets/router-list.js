define(['utils'], function (utils) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var selectedList = [];
    var columns = [{
        "data": "id",
        "name": "id",
        "orderable": false
    }, {
        "data": "name",
        "name": "name"
    }, {
        "data": "status",
        "name": "status"
    }, {
        "data": "external_gateway_info",
        "name": "external_gateway_info"
    }, {
        "data": "subnet_id",
        "name": "subnet_id"
    }];
    var columnDefs = [{
        targets: 0,
        render: function(data) {
            return '<label><input type="checkbox" name="'+data+'" router_id="'+data+'"></label>'
        }
    }, {
        targets: 1,
        render: function (data, type, item) {
            return '<a href="/admin/nets/router_detail?id=' + item.id + '">' + data + '</a>'
        }
    }, {
        targets: 2,
        render: function (data) {
            return data == 'ACTIVE' ? '可用' : '不可用';
        }
    }, {
        targets: 3,
        render: function (data) {
            if (data !== null) {
                if (data && data.external_fixed_ips[0].ip_address) {
                    return data.external_fixed_ips[0].ip_address
                }
            }
            return ''
        }
    }, {
        targets: 4,
        render: function (data) {
            return data.length;
        }
    }];
    var _datatable = utils.datatable($("#router_list"), {
        columns: columns,
        columnDefs: columnDefs
    }, {url: '/admin/describe_router', data: {owner: owner, zone: zone}});

    $("#router_list").find('tbody').on('click','input',function(){
        var router_id = $(this).attr('router_id');
        if($(this).is(':checked')){
            selectedList.push(router_id);
        }else{
            selectedList.splice(selectedList.indexOf(router_id),1);
        }
        setButton()
    });
    $(".selectedAll").on('click', function(){
        selectedList = [];
        var $listInput = $("#router_list").find('tbody').find('input');
        if($(this).is(':checked')){
            $listInput.prop('checked',true).each(function () {
                selectedList.push($(this).attr('router_id'));
            })
        }else{
            $listInput.removeProp('checked');
        }
        setButton()
    });
    function setButton(){
        if(selectedList.length == 0){
            $("#delete_router").prop("disabled", 'disabled');
            $("#edit_router").attr('disabled', 'disabled');
        }else if(selectedList.length == 1){
            $("#delete_router").removeProp("disabled");
            $("#edit_router").removeAttr("disabled");
        }else{
            $("#delete_router").removeProp("disabled");
            $("#edit_router").attr('disabled', 'disabled');
        }
    }

    $("#edit_router").click(function () {
        location.href = $(this).data('href') + '?id=' + selectedList[0];
    });
    $("#delete_router").click(function () {
        $('#delete_router_modal').modal();
    });
    $("#delete_router_btn").click(function () {
        utils._ajax({
            url: '/admin/delete_router',
            contentType: 'application/json',
            data: JSON.stringify({
                owner: $('#owner').val(),
                zone: $('#zone').val(),
                router_list: selectedList,
                action: "deleteRouter"
            }),
            succCB: function (result) {
                utils.succMsg("删除成功");
                $('#delete_router_modal').modal('hide');
                _datatable.ajax.reload();
            },
            errCB: function (result) {
                utils.errMsg(result.ret_msg);
            }
        });
    });
});