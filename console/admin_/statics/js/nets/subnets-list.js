define(['utils'], function(utils) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var $deleteText = $('#deleteText');
    var selectedList = [];
    var columns = [{
        "data": "name",
        "name": "name",
        "orderable": false
    }, {
        "data": "name",
        "name": "name"
    }, {
        "data": "cidr",
        "name": "cidr"
    }, {
        "data": "public",
        "name": "public"
    }, {
        "data": "instances",
        "name": "instances"
    }];
    var columnDefs = [{
        targets: 0,
        render: function(data, type, item) {
            return '<label><input type="checkbox" item='+JSON.stringify(item)+' /></label>'
        }
    }, {
        targets: 1,
        render: function(data, type, item) {
            return '<a href="/admin/nets/subnets_detail?id=' + item.id + '">' + data + '</a>';
        }
    }, {
        targets: 3,
        render: function(data) {
            return data ? '是' : '否';
        }
    }, {
        targets: 4,
        render: function(data) {
            return data.length;
        }
    }];
    var _datatable = utils.datatable($("#subnets_list"), {
        columns: columns,
        columnDefs: columnDefs
    }, {url: '/admin/subnet/describe_subnet',
        data: {owner: owner, zone: zone}
    },function(){
        selectedList = [];
        setButton()
    });
    $("#subnets_list").find('tbody').on('click','input[type=checkbox]',function(){
        var item = JSON.parse($(this).attr('item'));
        if($(this).is(':checked')){
            selectedList.push(item);
        }else{
            selectedList = selectedList.filter((json) => (json.id != item.id));
        }
        setButton()
    });
    $(".selectedAll").on('click', function(){
        selectedList = [];
        var $listInput = $("#subnets_list").find('tbody').find('input');
        if($(this).is(':checked')){
            $listInput.prop('checked',true).each(function () {
                selectedList.push(JSON.parse($(this).attr('item')));
            })
        }else{
            $listInput.removeProp('checked');
        }
        setButton()
    });
    function setButton(){
        if(selectedList.length > 0){
            $deleteText.html(`要删除的子网有${selectedList.map((item) => (item.name))}，总共包含${selectedList.map((item) => (item.instances_count)).reduce((a,b) => (a+b))}个主机，确认删除？`);
        }
        if(selectedList.length == 0){
            $("#delete_subnets").prop("disabled", 'disabled');
            $("#edit_subnets").attr('disabled', 'disabled');
        }else if(selectedList.length == 1){
            $("#delete_subnets").removeProp("disabled");
            $("#edit_subnets").removeAttr("disabled");
        }else{
            $("#delete_subnets").removeProp("disabled");
            $("#edit_subnets").attr('disabled', 'disabled');
        }
    }
    $("#delete_subnets").click(function() {
        $('#delete_subnets_modal').modal();
    });
    $("#edit_subnets").click(function() {
        location.href = $(this).data('href') + '?id=' + selectedList[0].id;
    });

    utils.refreshDataTable(_datatable);
    $("#delete_subnets_btn").click(function() {
        utils._ajax({
            url: '/admin/subnet/delete_subnet',
            contentType: 'application/json',
            data: JSON.stringify({
                owner: $('#owner').val(),
                zone: $('#zone').val(),
                subnet_list: selectedList.map((item) => ({subnet_id:item.id,network_id:item.network_id,name:item.name}))
            }),
            succCB: function(result) {
                utils.succMsg("删除成功");
                $('#delete_subnets_modal').modal('hide');
                _datatable.ajax.reload();
                selectedList = [];
            },
            errCB: function(result) {
                utils.errMsg(result.ret_msg);
            }
        });
    });
});
