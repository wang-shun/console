define(['utils'], function(utils) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var param = utils.getUrlParams();
    var name = decodeURIComponent(param.name);
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
            $("#name").html(data.name);
            $("#status").html(data == 'ACTIVE' ? '可用' : '不可用');
            $("#gateway").html(data.external_gateway_info ? data.external_gateway_info.external_fixed_ips[0].ip_address : '无');
            $("#nets").html('');
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
                    if (data[i].router_name == name) {
                        json.push(data[i]);
                    }
                }
            }
            console.log(json);
            var str = "";
            for (var i = 0, j = json.length; i < j; i++) {
                str += '<a href="/admin/nets/subnets_detail?id='+json[i].id+'">'+json[i].name+'</a> </br>'
            }
            $("#nets").html(str);
        }
    });
});