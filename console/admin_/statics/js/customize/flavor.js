define(['utils'], function (utils) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var selectedList = [];
    var columns = [{
        "data": "flavor_id",
        "name": "flavor_id",
        "orderable": false
    }, {
        "data": "name",
        "name": "name"
    }, {
        "data": "vcpus",
        "name": "vcpus"
    }, {
        "data": "ram",
        "name": "ram"
    }, {
        "data": "disk",
        "name": "disk"
    }, {
        "data": "public",
        "name": "public"
    }];
    var columnDefs = [{
        targets: 0,
        render: function(data, type, item) {
            return '<label><input type="checkbox" ispublic="'+item.public+'" name="'+data+'" flavor_id="'+data+'"></label>'
        }
    }, {
        targets: 1,
        render: function (data, type, item) {
            return '<a href="/admin/customize/flavor_detail?flavor_id=' + item.flavor_id + '">' + data + '</a>';
        }
    }, {
        targets: 5,
        render: function (data) {
            return data ? '是' : '否';
        }
    }];
    var _datatable = utils.datatable($("#flavor_list"), {
        columns: columns,
        columnDefs: columnDefs,
        order: [[1, 'desc']]
    }, {url: '/admin/api/', data: {action: 'DescribeInstanceTypes', owner: owner, zone: zone}});
    $("#flavor_list").find('tbody').on('click','input',function(){
        var flavor_id = $(this).attr('flavor_id');
        var ispublic = $(this).attr('ispublic');
        var data = {
            id: flavor_id,
            ispublic: ispublic
        }
        if($(this).is(':checked')){
            selectedList.push(data);
        }else{
            var index = selectedList.forEach(function(item,i){
                if(flavor_id == item.id){
                    return i;
                } 
            });
            selectedList.splice(index,1);
        }
        setButton()
    });
    $(".selectedAll").on('click', function(){
        selectedList = [];
        var $listInput = $("#flavor_list").find('tbody').find('input');
        if($(this).is(':checked')){
            $listInput.prop('checked',true).each(function () {
                var flavor_id = $(this).attr('flavor_id');
                var ispublic = $(this).attr('ispublic');
                var data = {
                    id: flavor_id,
                    ispublic: ispublic
                };
                selectedList.push(data);
            })
        }else{
            $listInput.removeProp('checked');
        }
        setButton()
    });
    function setButton(){
        if(selectedList.length == 0){
            $("#delete_flavor").prop("disabled", 'disabled');
            $("#edit_flavor").attr('disabled', 'disabled');
        }else if(selectedList.length == 1){
            $("#delete_flavor").removeProp("disabled");
            $("#edit_flavor").removeAttr("disabled");
        }else{
            $("#delete_flavor").removeProp("disabled");
            $("#edit_flavor").attr('disabled', 'disabled');
        }
    }
    $("#edit_flavor").click(function () {
        location.href = $(this).data('href') + '?flavor_id=' + selectedList[0].id;
    });
    $("#delete_flavor").click(function () {
        $('#delete_flavor_modal').modal();
    });
    utils.refreshDataTable(_datatable);
    $("#delete_flavor_btn").click(function () {
        utils._ajax({
            url: '/admin/api/',
            contentType: 'application/json',
            data: JSON.stringify({
                action: 'DeleteInstanceType',
                owner: $('#owner').val(),
                zone: $('#zone').val(),
                flavor_id: selectedList.map(function(item){
                    return item.id
                })
            }),
            succCB: function (result) {
                utils.succMsg("删除成功");
                $('#delete_flavor_modal').modal('hide');
                selectedList = [];
                _datatable.ajax.reload();
            },
            errCB: function (result) {
                utils.errMsg(result.ret_msg);
            }
        });
    });
});
