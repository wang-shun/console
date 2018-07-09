define(['utils', 'selectBox'], function (utils, SelectBox) {

    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var routerName = '';


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
                if(!data[i].router_name && data[i].gateway_ip){
                    json.push({'id': data[i]['id'], value: data[i]['name'], data: data[i]});
                }
            }
            box.setDataLeft(json);
        }
    });

    // 设置路由名称
    $("#create_router_name").on("blur", function () {
        routerName = $(this).val().trim();
        checkName(routerName);
    });
    // 点击创建
    $("#create_router").on("click", function () {
        if (!checkName(routerName)) {
            return false;
        }
        var enable_gateway = !!$("input[name=enable_gateway]:checked").val();
        var param = {
            owner: owner,
            zone: zone,
            name: routerName,
            enable_gateway: enable_gateway,
            action: 'createRouter',
            subnet_list: box.getData('right').map(function (net) {
                return net.id;
            })
        };
        utils._ajax({
            url: "/admin/create_router",
            contentType: 'application/json',
            data: JSON.stringify(param),
            succCB: function () {
                utils.succMsg('路由创建成功');
                location.href = '/admin/nets/router';
            },
            errCB: function (err) {
                utils.succMsg(err.ret_msg);
            },
            error: function () {
                utils.succMsg('路由创建失败');
            }
        });
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
