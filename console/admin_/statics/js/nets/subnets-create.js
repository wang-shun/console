// TODO 这里包含子网的列表展示,创建,修改,删除.逻辑
define(['utils', 'subnetGroup', 'selectBox'], function(utils, createSubnets, SelectBox) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var hasPublicNetHostList = [];
    var is_public = true;

    var CreateSubnets = new createSubnets();

    // 加载默认ip段
    CreateSubnets.loadIPGroupHTML();
    // 设置名称
    $("#create_subnets_name").on("blur", function() {
        CreateSubnets.setName($(this).val().trim());
        CreateSubnets.checkValue();
    });
    // 设置cidr_ip
    $("#create_subnets_cidr").on("blur", "input:lt(4)", function() {
        var cidr_arr = CreateSubnets.getCIDR_ip();
        var num = utils.num_to_min(utils.num_to_max($(this).val(), 255), 0);
        cidr_arr[$(this).attr('index')] = num;
        $(this).val(num);
        CreateSubnets.setCIDR_ip(cidr_arr);
        var cidr_mask = CreateSubnets.getCIDR_mask();
        if (cidr_mask != '') {
            $("#create_subnets_cidr").find('input').eq(4).blur();
        }
        CreateSubnets.checkValue();
    });
    // 设置cidr_mask
    $("#create_subnets_cidr").on("blur", "input:eq(4)", function() {
        var num = utils.num_to_min(utils.num_to_max($(this).val(), 30), 8);
        $(this).val(num);
        CreateSubnets.setCIDR_mask(num);
        CreateSubnets.loadCIDR_ip();
        var cidr_arr = CreateSubnets.getCIDR_ip();
        for (var i = 0; i < cidr_arr.length; i++) {
            $(this).parent().find('input[index=' + i + ']').val(cidr_arr[i]);
        }
        CreateSubnets.loadGateway();
        var gateway_arr = CreateSubnets.getGateway();
        var $createSubnetsGateway = $("#create_subnets_gateway");
        for (var i = 0; i < gateway_arr.length; i++) {
            $createSubnetsGateway.find('input[index=' + i + ']').val(cidr_arr[i]);
        }
        CreateSubnets.loadIPGroupTip();
        CreateSubnets.refIPGroupHTML();
        CreateSubnets.setIPGroupdata();
        CreateSubnets.checkValue();
    });
    // 是否公开
    $("#open_gateway").click(function () {
        $("#box-select-content").hide();
        $("#open_gateway").addClass("active");
        $("#close_gateway").removeClass("active");
        is_public = true;
    });
    $("#close_gateway").click(function () {
        $("#box-select-content").show();
        $("#open_gateway").removeClass("active");
        $("#close_gateway").addClass("active");
        is_public = false;
    });
    // 删除ip段
    $("#switch_ivp4_list").on("click", ".delete-ip", function() {
        var index = $(this).parent().index();
        CreateSubnets.deleteIP(index);
    });
    // 添加ip段
    $("#switch_ivp4_list").on("click", ".add-ip", function() {
        CreateSubnets.addIP();
    });
    // ip段修改时
    $("#create_subnets_ip_group").on('blur', '.box-list-input-ips input', function() {
        var max = $('.box-list-input-ips input').index($(this)) === 7 ? 254 : 255;
        var num = utils.num_to_min(utils.num_to_max($(this).val(), max), 0);
        $(this).val(num);
        CreateSubnets.setIPGroupdata();
        CreateSubnets.checkValue();
    });
    var box = new SelectBox({
        container: $("#box-select-box"), // 用于生成插件的父元素
        leftTitle: "人员名单",
        rightTitle: "可见人员名单",
        isSearchable: true,
        dataList: [
            [], // 左侧列表
            []  // 右侧列表
        ]
    });

    utils._ajax({
        url: "/finance/api/",
        data: {
            action: 'DescribeDepartmentMember',
            data: {
                department_id: "dep-00000001"
            },
            owner: owner,
            zone: zone,
            timestamp: new Date().getTime(),
        },
        succCB: function (result) {
            var data = result.ret_set.member_list;
            for (var i = 0, j = data.length; i < j; i++) {
                box.setDataLeft([{'id': data[i]['id'], value: data[i]['name']}]);
            }
        }
    });
    // 点击创建时
    $("#create_subnets").on('click', function() {
        var param = CreateSubnets.checkValue();
        if (param) {
            param.owner = owner;
            param.zone = zone;
            param.user_list = box.getData('right').map(function(item) {
                return item.id;
            }).join(',');
            param.network_mode = $("#create_network_mode").val();
            param.public = is_public;
            delete param.network_mode;
            delete param.gateway_ip;

            console.log(param);
            utils._ajax({
                url: "/admin/subnet/create_subnet",
                contentType: 'application/json',
                data: JSON.stringify(param),
                succCB: function() {
                    utils.succMsg('子网创建成功');
                    location.href = '/admin/nets/subnets';
                },
                errCB: function(err) {
                    utils.errMsg(err.ret_msg);
                },
                error: function() {
                    utils.errMsg('子网创建失败');
                }
            });
        } else {
            utils.errMsg('参数错误创建子网失败');
        }
    });
    function checkHasPublicNetHost(host) {
        if (!gatewayBoolean) {
            return false;
        }
        var currentResult = host && host.pub_subnet;
        box.getData('right').map(function(item) {
            if (item.data && item.data.pub_subnet) {
                hasPublicNetHostList.push(item);
            }
        });
        return currentResult || (hasPublicNetHostList.length > 1);
    }
});