/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function (utils) {
    var selectedList = ''; // 选中物理机名称
    var selectedSource = ''; // 获取选中资源池名称
    var selectedIPMI = ''; // 获取选中的IPMI地址
    var statusSource = {'on': '运行中', 'off': '关机中', 'move': '迁移中'};
    var param = utils.getUrlParams();
    var pool_name = '';
    if (param.name) {
        pool_name = decodeURIComponent(param.name);
    }
    var columns = [{
        "data": "hostname",
        "name": "hostname",
    }, {
        "data": "status",
        "name": "status"
    }, {
        "data": "model",
        "name": "model",
    }, {
        "data": "ipmi_ip",
        "name": "ipmi_ip",
    }, {
        "data": "compute_pool",
        "name": "cluster_belong_to"
    }, {
        "data": "load",
        "name": "load",
    }, {
        "data": "hostname",
        "name": "hostname",
    }, {
        "data": "uptime",
        "name": "run_time",
    }
    ];
    var columnDefs = [{
        targets: 7,
        render: function (data) {
            return utils.numToDate(data);
        }
    }, {
        targets: 1,
        render: function (data) {
            //return statusSource[data] || '异常';
            return '正常';
        }
    }, {
        targets: 0,
        render: function (data) {
            return "<a href='/admin/sourceManage/physicsSourceDetail?sourceName="+data+"'>"+data+"</a>";
        }
    }, {
        targets: 6,
        render: function (data, type, row) {
            var vm_amount = 0;
            utils._ajax({
                url: '/admin/pools/compute_resource/list_instance',
                data: {
                    owner: $("#owner").val(),
                    zone: $("#zone").val(),
                    start: 0,
                    length: 1000,
                    flag: 'host',
                    name: data
                },
                finalCB: function (result) {
                    vm_amount = result.data.length;
                    var strHost = $("#span_" + data).html();
                    if (!/\(\w+\)/.test(strHost)) {
                        $("#span_" + data).attr({"vm_amount":vm_amount}).html('虚拟机(' + vm_amount + ')');
                    }
                }
            });
            return "<a class='vm_amount' id='span_" + data + "' href='/admin/sourceManage/virtualList?flag=host&name="+data+"'>虚拟机()</a>";
        }
    }];
    var _datatable = utils.datatable($("#physicsSourceTable"), {
        columns: columns,
        columnDefs: columnDefs
    }, {url: '/admin/physical_machine/list/api', data: {pool_name: pool_name}});

    utils.tableClick($("#physicsSourceTable").find('tbody'), {
        offCB: function (obj) {
            selectedList = '';
            selectedSource = '';
            selectedIPMI = '';
            $("#open-computer,#id-close-computer,#ipmi,#move_virtual").prop("disabled", true);
        },
        onCB: function (obj) {
            var rowData = _datatable.row(obj).data();
            hostId = rowData.hostname.match(/[^>]+(?=(?:\<|$))/g)[0];
            hostStatus = rowData.status;
            selectedList = hostId;
            selectedSource = rowData.compute_pool;
            selectedIPMI = rowData.ipmi_ip;
            var vm_amount = obj.find('.vm_amount').attr('vm_amount');
            $('#progressNum').html('0/' + vm_amount);
            if (hostStatus == 'on') {
                // 已开机
                $("#open-computer").prop("disabled", true);
                $("#ipmi").prop("disabled", false);
                $("#id-close-computer").prop("disabled", vm_amount != 0);
                $("#move_virtual").prop("disabled", vm_amount == 0);
            } else if (hostStatus == 'off') {
                // 已关机
                $("#open-computer").prop("disabled", false);
                $("#id-close-computer").prop("disabled", true);
                $("#move_virtual").prop("disabled", true);
                $("#ipmi").prop("disabled", false);
            } else if (hostStatus == 'move') {
                // 迁出中
                $("#open-computer").prop("disabled", true);
                $("#id-close-computer").prop("disabled", true);
                $("#move_virtual").prop("disabled", true);
                $("#ipmi").prop("disabled", true);
            }
        }
    });

    // 开机按钮操作
    $('#open-computer').on('click', function () {
        utils._ajax({
            url: '/admin/physical_machine/boot/api',
            data: {physical_machine_id: hostId},
            succCB: function (result) {
                var interval = setInterval(function () {
                    utils._ajax({
                        url: '/admin/physical_machine/status/api',
                        data: {physical_machine_id: id},
                        succCB: function (data) {
                            if (data.ret_set[0] != hostStatus) {
                                clearInterval(interval);
                                utils.succMsg("开机成功");
                                $('input:checked').parent().next().next().text(hostStatus);
                                location.reload();
                            }
                        },
                        errCB: function () {
                            utils.errMsg("开机失败请重试");
                        },
                        error: function () {
                            utils.errMsg("开机失败请重试");
                        }
                    });
                }, 2000);
            }
        });
    });

    // 关机操作
    $("#id-close-computer").on('click', function () {
        $("#hostIds").html(selectedList);
        $('#id-close-computer-modal').modal({
            backdrop: 'static',
            keyboard: true
        });
        $('#shutBtn').on('click', function () {
            utils._ajax({
                url: '/admin/physical_machine/halt/api',
                data: {physical_machine_hostname: selectedList, action: 'HaltPhysicalMachine'},
                succCB: function () {
                    utils.succMsg("关机成功");
                    location.reload();
                },
                errCB: function () {
                    utils.errMsg("关机失败请重试");
                },
                finalCB: function () {
                    $('#id-close-computer-modal').modal('hide');
                },
                error: function () {
                    utils.errMsg("关机失败请重试");
                }
            });
        });
    });


    // 获取待迁移机列表函数
    function getAllVmlist(selectedList) {
        var nowVirtualMoveCount = 0; // 目前还剩下几台需要迁移的主机
        utils._ajax({
            url: '/admin/pools/compute_resource/list_instance',
            data: {
                start:0,
                length:1000,
                name:selectedList,
                flag:'host'
            },
            finalCB: function (result) {
                var vmCatch = {};
                var allVmList = result.data.filter(function(item){
                    return item.instance_state === 'active'
                });
                var $vmListTr = $('#closeComputerVirtualList').find('tbody').find('tr');
                nowVirtualMoveCount = allVmList.length;
                // 处理进度条与百分比
                for (var i = 0; i < nowVirtualMoveCount; i++) {
                    if (virtualMoveList.indexOf(allVmList[i].name) != '-1') {
                        if (allVmList[i].instance_state == 'error') {
                            vmCatch[allVmList[i].name] = 'error';
                            // 遇到迁移错误机器应当将总数减一
                            nowVirtualMoveCount--;
                        } else {
                            vmCatch[allVmList[i].name] = 'moving';
                        }

                    }

                }


                for (var j = 0; j < $vmListTr.length; j++) {
                    var vmState = '<span class="text-success">迁移成功</span>';
                    var $vmListTrName = $vmListTr.eq(j).find('td').eq(0).html();
                    if (vmCatch[$vmListTrName] === 'moving') {
                        vmState = '<span class="text-warning">迁移中</span>';
                    } else if (vmCatch[$vmListTrName] === 'error') {
                        vmState = '<span class="text-danger">迁移失败</span>';
                    }
                    $vmListTr.eq(j).find('td').eq(3).html(vmState);
                }

                var bili = (virtualMoveCount - nowVirtualMoveCount) / virtualMoveCount;
                if (nowVirtualMoveCount == 0) {
                    clearInterval(moveVirtualInterval);
                    bili = 1;
                    utils.succMsg("全部迁移成功");
                    setTimeout(function () {
                        location.reload();
                    }, 1000);
                }
                $("#migrateProgress").css('width', bili * 100 + '%');
                $("#progressNum").html((virtualMoveCount - nowVirtualMoveCount) + '/' + virtualMoveCount);
            }
        });
    }

    var virtualMoveList = []; // 待迁移虚拟机列表
    var virtualMoveCount = 0; // 等待主机迁移个数
    var moveVirtualInterval = null; // 迁移定时器
    $('#move_virtual').on('click', function () {
        $('#id-move-computer-modal').modal({
            backdrop: 'static',
            keyboard: true
        });
        $('#closeComputerVirtualList').find('tbody').html('<tr><td colspan=4 style="text-align:center">正在获取虚拟机信息，请稍等。。。</td></tr>');
        $('#moveVirtualsubmitBtn').addClass('disabled');
        utils._ajax({
            url: '/admin/physical_machine/hostname_list/api',
            data: {
                owner: 'admin1',
                action: 'DescribePhysicalMachineHostnameList',
                pool_name: selectedSource
            },
            succCB: function (result) {
                var data = result.ret_set.host_list;
                if (data.length > 1) {
                    // 当资源池主机大于一个时才可以迁移
                    $('#moveVirtualsubmitBtn').removeClass('disabled');
                    DescribePhysicalMachineAllVmListFun();
                } else {
                    $('#closeComputerVirtualList').find('tbody').html('<tr><td colspan=4 style="text-align:center">资源池下只有一台主机，无法迁移虚拟机。</td></tr>');
                }
            }
        });
    });
    function DescribePhysicalMachineAllVmListFun() {
        utils._ajax({
            url: '/admin/pools/compute_resource/list_instance',
            data: {
                owner: $("#owner").val(),
                zone: $("#zone").val(),
                start: 0,
                length: 1000,
                flag: 'host',
                name: selectedList
            },
            finalCB: function (result) {
                var allVmList = result.data.filter(function(item){
                    return item.instance_state === 'active'
                });
                var strVm = '';
                virtualMoveCount = allVmList.length;
                for (var i = 0; i < virtualMoveCount; i++) {
                    virtualMoveList.push(allVmList[i].name);
                    strVm += '<tr vmname="' + allVmList[i].name + '"><td>' + allVmList[i].name + '</td><td>' + allVmList[i].instance_type + '</td><td>' + allVmList[i].image + '</td><td class="text-warning">等待迁移</td></tr>';
                }
                $('#progressNum').html('0/' + virtualMoveCount);
                $('#closeComputerVirtualList').find('tbody').html(strVm);
            }
        });
    }

    // 开始迁移操作
    $('#moveVirtualsubmitBtn').on('click', function () {
        // 迁移主机接口
        if ($(this).hasClass('disabled')) {
            return false;
        }
        $(this).addClass('disabled');
        function moveVirtual() {
            utils._ajax({
                type: 'post',
                url: '/admin/host_disperse/api',
                data: {
                    owner: 'admin1',
                    action: 'DescribePhysicalMachineHostnameList',
                    src_physical_machine: selectedList
                },
                succCB: function () {
                    moveVirtualInterval = setInterval(function () {
                        getAllVmlist(selectedList);
                    }, 3000);
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
        }

        moveVirtual();
    });

    // IPMI展示
    $('#ipmi').on('click', function () {
        var httpsStr = "https://" + selectedIPMI;
        var calTop = $("window").height() / 2 - 450 / 2;
        var calLeft = $("window").width() / 2 - 750 / 2;
        window.open(httpsStr, '', 'height=450, width=750, top=' + calTop + ',left=' + calLeft + ', toolbar=no, menubar=no, scrollbars=no, resizable=no,location=no, status=no');
    });
    // 刷新
    $("#refresh").on("click", function () {
        location.reload();
    });

    // 获取全部的计算资源池
    utils._ajax({
        type: 'post',
        url: '/admin/pools/compute_resource/list',
        data: {
            owner: $('#owner').val(),
            zone: $('#zone').val(),
            flag: 0,
            start: 0,
            length: 1,
        },
        finalCB: function (result) {
            var list = result.data;
            var str = '<option value="" selected>全部</option>';
            list.forEach(function (item) {
                str += '<option value="' + item.name + '">' + item.name + '</option>';
            });
            str += '<option value="default">default</option>';
            $("#pool_list").html(str);
            var name = decodeURIComponent(param.name);
            if (name) {
                $('#pool_list').find("option[value='" + name + "']").attr('selected', true);
            } else {
                $('#pool_list').find("option[value='']").attr('selected', true);
            }
        }
    });

    $("#pool_list").change(function () {
        var name = $(this).val();
        location.href = location.href.replace(/(\?.+)?$/, (name ? '?name=' + name : ''));
    });
});
