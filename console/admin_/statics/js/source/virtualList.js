/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function (utils) {
    var param = utils.getUrlParams();
    var id = '';
    if (param.name) {
        id = decodeURIComponent(param.name);

    }
    var selectedVm = [];
    var pool = "";
    var host = "";
    var active = "";
    var columns = [{
        "data": "name",
        "name": "name",
        "orderable": false
    }, {
        "data": "name",
        "name": "name"
    }, {
        "data": "instance_state",
        "name": "instance_state"
    }, {
        "data": "addresses",
        "name": "addresses"
    }, {
        "data": "instance_type",
        "name": "instance_type"
    }, {
        "data": "image",
        "name": "image"
    }, {
        "data": "pool",
        "name": "pool"
    }, {
        "data": "phy_host",
        "name": "phy_host"
    }, {
        "data": "launched_at",
        "name": "launched_at"
    }
    ];
    var columnDefs = [{
        targets: 0,
        render: function (data,i,item) {
            return '<label><input type="checkbox" name="' + data + '" pool="'+item.pool+'" host="'+item.phy_host+'" active="'+item.instance_state+'"></label>'
        }
    }, {
        targets: 8,
        render: function (data) {
            var nowDate = new Date().getTime();
            return utils.numToDate(nowDate - data * 1000);
        }
    }];
    var _datatable = utils.datatable($("#virtualList"), {
        columns: columns,
        columnDefs: columnDefs,
        order: [[1, 'desc']]
    }, {
        url: '/admin/pools/compute_resource/list_instance',
        data: {name: id, flag: param.flag},
    }, function(){
        selectedVm = [];
        pool = '';
        host = '';
        setButton()
    });
    $("#virtualList").find('tbody').on('click', 'input', function () {
        var name = $(this).attr('name');
        pool = $(this).attr('pool');
        host = $(this).attr('host');
        active = $(this).attr('active');
        if ($(this).is(':checked')) {
            selectedVm.push(name);
        } else {
            selectedVm.splice(selectedVm.indexOf(name), 1);
            pool = '';
            host = '';
            active = '';
        }
        setButton()
    });
    $(".sorting_disabled").on('click', ".selectedAll", function () {
        selectedVm = [];
        pool = '';
        host = '';
        active = '';
        var $listInput = $("#virtualList").find('tbody').find('input');
        if ($(this).is(':checked')) {
            $listInput.prop('checked', true).each(function () {
                selectedVm.push($(this).attr('name'));
            })
        } else {
            $listInput.removeProp('checked');
        }
        setButton()
    });
    function setButton() {
        if (selectedVm.length == 0) {
            $("#virtualMoveBtn").prop("disabled", true);
            $("#delete_virtual").prop("disabled", true);
            $("#virtualName").html('');
            $('#virtualPool').html('');
        } else if (selectedVm.length == 1) {
            $("#virtualMoveBtn").removeProp("disabled");
            $("#delete_virtual").removeProp("disabled");
            $("#virtualName").html(selectedVm[0]);
            $('#virtualPool').html(pool);
        } else {
            $("#virtualMoveBtn").prop("disabled", true);
            $("#delete_virtual").removeProp("disabled");
            $("#virtualName").html('');
            $('#virtualPool').html('');
        }
    }

    $('#virtualMoveBtn').on('click', function () {
        utils._ajax({
            url: '/admin/physical_machine/hostname_list/api',
            data: {
                owner: 'admin1',
                action: 'DescribePhysicalMachineHostnameList',
                pool_name: pool
            },
            succCB: function (result) {
                var data = result.ret_set.host_list;
                var indexOf = data.indexOf(host);
                if (indexOf !== -1) {
                    data.splice(indexOf, 1);
                }
                if (data.length) {
                    $('#virtualHost').html('<option>' + data.join('</option><option>') + '</option>');
                    $('#virtualMoveSubmit').removeClass('disabled');
                } else {
                    $('#virtualHost').html('<option>---没有可迁移主机，请联系管理员---</option>').prop("disabled", true);
                    $('#virtualMoveSubmit').addClass('disabled');
                }
            }
        });

        $('#virtualMoveModal').modal({
            backdrop: 'static',
            keyboard: true
        });
    });

    $('#virtualMoveSubmit').on('click', function () {
        if ($(this).hasClass('disabled')) {
            return false;
        }
        if (active != 'active'){
            alert('非active虚拟机无法进行迁移');
            return false;
        }
        utils._ajax({
            url: '/admin/host_migrate/api',
            data: {
                owner: 'admin1',
                action: 'DescribePhysicalMachineHostnameList',
                instance_id: $('#virtualName').html(),
                dst_physical_machine: $('#virtualHost').val()
            },
            succCB: function () {
                $('#virtualMoveModal').modal('hide');
                utils.succMsg("迁移成功");
                setTimeout(function () {
                    $("#virtualList").find('tbody').empty();
                    location.reload();
                }, 1000);
            },
            errCB: function () {
                utils.errMsg("迁移失败");
                $(this).removeClass('disabled');
            },
            error: function () {
                utils.errMsg("迁移失败");
                $(this).removeClass('disabled');
            }
        });
    });
    // 刷新
    $("#refresh").on("click", function () {
        location.reload();
    });
    $("#delete_virtual").on('click', function () {
        $("#delete_virtual_modal").modal();
    });
    $("#delete_virtual_btn").on('click', function () {
        utils._ajax({
            url: '/console/api',
            contentType: 'application/json',
            data: JSON.stringify({
                owner: $("#owner").val(),
                zone: $("#zone").val(),
                action: 'DeleteInstances',
                isSuperUser: true,
                instances: selectedVm,
            }),
            succCB: function () {
                utils.succMsg("删除成功");
            },
            errCB: function () {
                utils.errMsg("删除失败");
            },
            finalCB: function () {
                utils.succMsg("全部删除完成");
                location.reload();
            },
        });

    })
});
