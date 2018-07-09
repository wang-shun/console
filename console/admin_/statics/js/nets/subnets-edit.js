define(['utils', 'selectBox'], function(utils, SelectBox) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var param = utils.getUrlParams();
    var hasPublicNetHostList = [];
    var gatewayBoolean;
    var subnetObj = null;
    var is_public = true;

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

    // 请求子网详情接口
    function getSubnetAjax() {
        utils._ajax({
            url: "/admin/subnet/describe_subnet",
            data: {
                owner: owner,
                zone: zone,
                subnet_name: param.id
            },
            finalCB: function(obj) {
                subnetObj = obj.data[0];
                loadSubnetData(subnetObj);
                // 查询用户列表
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
                        var member_list = result.ret_set.member_list;
                        for (var i = 0, j = member_list.length; i < j; i++) {
                            if (subnetObj.owner_list.indexOf(member_list[i]['id']) != -1) {
                                box.setDataRight([{'id': member_list[i]['id'], value: member_list[i]['name']}]);
                            } else {
                                box.setDataLeft([{'id': member_list[i]['id'], value: member_list[i]['name']}]);
                            }
                        }
                    }
                });
            }
        });
    }

    // 加载所有数据
    function loadSubnetData(subnet) {
        var data = {};
        data.name = subnet.name;
        data.router = subnet.router_name;
        data.cidr = subnet.cidr;
        data.gateway = subnet.gateway_ip;
        data.ipgroup = subnet.allocation_pools;
        data.dns = subnet.dns_nameservers.join('，');
        data.instances = subnet.instances_id;
        data.public = subnet.public;
        gatewayBoolean = !!subnet.gateway_ip;

        loadSubnetHTML(data);
    }
    // 渲染可编辑子网
    function loadEditIpgroup(ipgroup, cidr) {
        var html_str = "";
        var cidr_ip = cidr.split('/')[0].split('.');
        var cidr_mask = parseInt(cidr.split('/')[1]);

        if(ipgroup.length ==1){
            var ip_start = ipgroup[0].start.split('.');
            var ip_end = ipgroup[0].end.split('.');
            html_str += '<div class="box-list-input-ips">' +
                '<div class="box-from-input-ip">' +
                '<input type="text" value="' + ip_start[0] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_start[1] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_start[2] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_start[3] + '" />' +
                '</div>' +
                '<span class="box-from-inline">至</span>' +
                '<div class="box-from-input-ip">' +
                '<input type="text" value="' + ip_end[0] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_end[1] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_end[2] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_end[3] + '" />' +
                '</div>' +
                '<a href="javascript:;" class="add-ip">' +
                '<span class="glyphicon glyphicon-plus-sign"></span>' +
                '添加IP段' +
                '</a>' +
                '<i class="box-list-error"></i>' +
                '</div>';
        }else{
            for (var i = 0, j = ipgroup.length; i < j; i++) {
                var ip_start = ipgroup[i].start.split('.');
                var ip_end = ipgroup[i].end.split('.');
                if(i !== (ipgroup.length-1)){
                    html_str += '<div class="box-list-input-ips">' +
                    '<div class="box-from-input-ip">' +
                    '<input type="text" value="' + ip_start[0] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_start[1] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_start[2] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_start[3] + '" />' +
                    '</div>' +
                    '<span class="box-from-inline">至</span>' +
                    '<div class="box-from-input-ip">' +
                    '<input type="text" value="' + ip_end[0] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_end[1] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_end[2] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_end[3] + '" />' +
                    '</div>' +
                    '<a href="javascript:;" class="delete-ip">' +
                    '<span class="glyphicon glyphicon-trash"></span>' +
                    '删除' +
                    '</a>' +
                    '<i class="box-list-error"></i>' +
                    '</div>';
                }else{
                    html_str += '<div class="box-list-input-ips">' +
                    '<div class="box-from-input-ip">' +
                    '<input type="text" value="' + ip_start[0] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_start[1] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_start[2] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_start[3] + '" />' +
                    '</div>' +
                    '<span class="box-from-inline">至</span>' +
                    '<div class="box-from-input-ip">' +
                    '<input type="text" value="' + ip_end[0] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_end[1] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_end[2] + '" />' +
                    '<span>.</span>' +
                    '<input type="text" value="' + ip_end[3] + '" />' +
                    '</div>' +
                    '<a href="javascript:;" class="add-ip">' +
                    '<span class="glyphicon glyphicon-plus-sign"></span>' +
                    '添加IP段' +
                    '</a>' +
                    '<i class="box-list-error"></i>' +
                    '</div>';
                }
            }
        }
        $("#subnets_ip_group").html(html_str);
        if (cidr_mask >= 0 && cidr_mask < 8) {
            $('.box-list-input-ips').find('.box-from-input-ip').find('input:lt(0)').attr('disabled', 'disabled');
        } else if (cidr_mask >= 8 && cidr_mask < 16) {
            $('.box-list-input-ips').find('.box-from-input-ip').find('input:lt(1)').attr('disabled', 'disabled');
        } else if (cidr_mask >= 16 && cidr_mask < 24) {
            $('.box-list-input-ips').find('.box-from-input-ip').find('input:lt(2)').attr('disabled', 'disabled');
        } else {
            $('.box-list-input-ips').find('.box-from-input-ip').find('input:lt(3)').attr('disabled', 'disabled');
        }
        $("#subnets_ip_group").on('click', '.add-ip', function() {
            var newStr = '<div class="box-list-input-ips">' +
                '<div class="box-from-input-ip">' +
                '<input type="text" value="' + ip_start[0] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_start[1] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_start[2] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_start[3] + '" />' +
                '</div>' +
                '<span class="box-from-inline">至</span>' +
                '<div class="box-from-input-ip">' +
                '<input type="text" value="' + ip_end[0] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_end[1] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_end[2] + '" />' +
                '<span>.</span>' +
                '<input type="text" value="' + ip_end[3] + '" />' +
                '</div>' +
                '<a href="javascript:;" class="add-ip">' +
                '<span class="glyphicon glyphicon-plus-sign"></span>' +
                '添加IP段' +
                '</a>' +
                '<i class="box-list-error"></i>' +
                '</div>';
            $("#subnets_ip_group").append($(newStr));
            var add_ip_length = $("#subnets_ip_group").find('.add-ip').length;
            $("#subnets_ip_group").find('.add-ip:lt(' + (add_ip_length - 1) + ')').addClass('delete-ip').removeClass('add-ip').html('<span class="glyphicon glyphicon-trash"></span>删除');

        });
        $("#subnets_ip_group").on('click', '.delete-ip', function() {
            $(this).parent().remove();
        });
    }
    //渲染不可编辑子网
    function loadShowIpgroup(arr) {
        var str = '';
        for(var i=0;i<arr.length;i++){
            str += arr[i].start + ' 至 ' + arr[i].end + '<br />';
        }
        $("#subnets_ip_group").html(str);
    }
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
    // 将数据渲染至页面
    function loadSubnetHTML(data) {
        $("#subnets_name").val(data.name);
        $("#subnets_cidr").html(data.cidr);
        $("#subnets_ip_group").html(data.ipgroup);
        $("#subnets_dns").html(data.dns);
        $("#host_list").html(data.instances.join(', ') || '-');
        if(data.public){
            $("#open_gateway").click();
        }else{
            $("#close_gateway").click();
        }
        if(data.instances.length>0){
            $("#tip").show();
            loadShowIpgroup(data.ipgroup);
        }else{
            $("#tip").hide();
            loadEditIpgroup(data.ipgroup, data.cidr);
        }
    }
    // 初始化页面函数
    function init() {
        getSubnetAjax();
    }
    init();
    // 点击修改时
    $("#edit_subnets").on('click', function() {
        if (param) {
            param.owner = owner;
            param.zone = zone;
            param.name = subnetObj.name;
            param.subnet_id = subnetObj.id;
            param.subnet_name = $("#subnets_name").val();
            param.allocation_pools = getIPGroups();
            param.network_id = subnetObj.network_id;
            param.public = is_public;
            param.user_list = box.getData('right').map(function(item) {
                return item.id;
            }).join(',');
            delete param.id;
            utils._ajax({
                url: "/admin/subnet/update_subnet",
                contentType: 'application/json',
                data: JSON.stringify(param),
                succCB: function() {
                    utils.succMsg('子网修改成功');
                    location.href = '/admin/nets/subnets';
                },
                errCB: function(err) {
                    utils.errMsg(err.ret_msg);
                },
                error: function() {
                    utils.errMsg('子网修改失败');
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
    function getIPGroups() {
        var ipGroupArr = [];
        $("#subnets_ip_group").find('.box-list-input-ips').each(function() {
            var inputGroupJSON = {};
            var $startInput = $(this).find('.box-from-input-ip').eq(0).find('input');
            var $endInput = $(this).find('.box-from-input-ip').eq(1).find('input');
            inputGroupJSON.start = [
                $startInput.eq(0).val(),
                $startInput.eq(1).val(),
                $startInput.eq(2).val(),
                $startInput.eq(3).val()
            ];
            inputGroupJSON.end = [
                $endInput.eq(0).val(),
                $endInput.eq(1).val(),
                $endInput.eq(2).val(),
                $endInput.eq(3).val()
            ];
            inputGroupJSON.start = inputGroupJSON.start.join('.');
            inputGroupJSON.end = inputGroupJSON.end.join('.');
            ipGroupArr.push(inputGroupJSON);
        });
        return ipGroupArr;
    }
});