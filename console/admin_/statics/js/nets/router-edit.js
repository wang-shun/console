define(['utils', 'selectBox'], function (utils, SelectBox) {

    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var param = utils.getUrlParams();
    var name = "";
    var used_nets = [];  // 所有未用过的net
    var load_nets = [];  // 本个路由使用的net
    var box = new SelectBox({
        container: $("#box-select-box"),
        leftTitle: "所有可用子网",
        rightTitle: "已加入子网",
        isSearchable: true,
        dataList: [[], []],
        event: {
            addListPreCallback: function (item, data) {
                return true;
            }
        }
    });
    utils._ajax({
        url: "/console/api",
        data: {
            action: 'DescribeNets',
            owner: owner,
            zone: zone
        },
        finalCB: function (result) {
            var data = result.ret_set;
            var json = [];
            for (var i = 0, j = data.length; i < j; i++) {
                if(data[i].gateway_ip){
                    var json = {'id': data[i]['id'], value: data[i]['name'], data: data[i]};
                    if (data[i].router_name == name) {
                        load_nets.push(json);
                    }
                    if (!data[i].router_name) {
                        used_nets.push(json);
                    }
                }
            }
            box.setDataLeft(used_nets);
            box.setDataRight(load_nets);
        }
    });

    utils._ajax({
        url: "/admin/describe_router",
        data: {
            action: 'DescribeNets',
            owner: owner,
            zone: zone,
            router_id: decodeURIComponent(param.id)
        },
        finalCB: function (result) {
            var data = result.data[0];
            name = data.name;
            $("#name").val(data.name);
            $("#router_gateway").html(data.external_gateway_info ? data.external_gateway_info.external_fixed_ips[0].ip_address : '无');
        }
    });

    // 设置路由名称
    $("#name").on("blur", function () {
        checkName($(this).val().trim());
    });
    // 点击确定
    $("#create_router").on("click", function () {
        if (!checkName(name)) {
            return false;
        }
        var change_net_list = box.getChangedData('right');
        var add_net_list = [];
        var del_net_list = [];
        for (var i = 0, j = change_net_list.length; i < j; i++) {
        if (change_net_list[i].type == 'add') {
            add_net_list.push(change_net_list[i].data.id);
        }
        if (change_net_list[i].type == 'remove') {
            del_net_list.push(change_net_list[i].data.id);
        }
        }

        var COUNT = 0;
        if (name !== $("#name").val()) {
            utils._ajax({
                url: "/admin/update_router",
                async: true,
                data: {
                    owner: $("#owner").val(),
                    zone: $("#zone").val(),
                    name: $("#name").val(),
                    router_id: decodeURIComponent(param.id),
                    action: "updataRouter",
                },
                succCB: function () {
                    utils.succMsg('路由名称修改成功');
                },
                errCB: function (err) {
                    utils.errMsg(err.ret_msg);
                },
                error: function () {
                    utils.errMsg('路由名称修改失败');
                }
            });
        }
        href_list();
        if (add_net_list.length > 0) {
            utils._ajax({
                url: "/admin/join_router",
                contentType: 'application/json',
                data: JSON.stringify({
                    owner: $("#owner").val(),
                    action:'joinRouter',
                    zone: $("#zone").val(),
                    router_id: decodeURIComponent(param.id),
                    subnet_list: add_net_list
                }),
                succCB: function () {
                    utils.succMsg('路由添加子网成功');
                    href_list();
                },
                errCB: function (err) {
                    utils.errMsg(err.ret_msg);
                },
                error: function () {
                    utils.errMsg('路由添加子网失败');
                }
            });
        } else {
            href_list();
        }
        if (del_net_list.length > 0) {
            utils._ajax({
                url: "/admin/quit_router",
                contentType: 'application/json',
                data: JSON.stringify({
                    owner: $("#owner").val(),
                    zone: $("#zone").val(),
                    action:'quitRouter',
                    router_id: decodeURIComponent(param.id),
                    subnet_list: del_net_list
                }),
                succCB: function () {
                    utils.succMsg('路由删除子网成功');
                    href_list();
                },
                errCB: function (err) {
                    utils.errMsg(err.ret_msg);
                },
                error: function () {
                    utils.errMsg('路由删除子网失败');
                }
            });
        } else {
            href_list();
        }
        function href_list() {
            COUNT++;
            if (COUNT >= 3) {
                location.href = '/admin/nets/router';
            }
        }
    });

    function checkName(name) {
        if (/^\s*$/.test(name)) {
            $("#create_router_name").parent().find('.box-list-error').html('名称不能为空');
            return false;
        } else {
            $("#create_router_name").parent().find('.box-list-error').html('');
            return true;
        }
    }

});
