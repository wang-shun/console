define(['utils'], function(utils) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var param = utils.getUrlParams();
    var data = {};

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
                var subnet = obj.data[0];
                loadSubnetData(subnet);
            }
        });
    }
    // 加载所有数据
    function loadSubnetData(subnet) {
        data.name = subnet.name;
        data.cidr = subnet.cidr;
        data.ipgroup = subnet.allocation_pools;
        data.dns = subnet.dns_nameservers.join('，');
        data.instances = subnet.instances_id;
        data.owner_list = subnet.owner_list;
        data.public = subnet.public;
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
                var member_json = {};
                for (var i = 0, j = member_list.length; i < j; i++) {
                    member_json[member_list[i].id] = member_list[i].name;
                }
                data.owner_list = data.owner_list.map((v) => (member_json[v])).join(', ');
                $("#owner_list").html(data.owner_list);
            }
        });
        loadSubnetHTML(data);
    }
    function getIpgrop(arr){
        var str = '';
        for(var i=0;i<arr.length;i++){
            str += arr[i].start + ' 至 ' + arr[i].end + '<br />';
        }
        return str;
    }
    // 将数据渲染至页面
    function loadSubnetHTML(data) {
        $("#subnets_name").html(data.name);
        $("#subnets_cidr").html(data.cidr);
        $("#subnets_ip_group").css('height','auto').html(getIpgrop(data.ipgroup));
        $("#subnets_dns").html(data.dns || '-');
        $("#is_public").html(data.public ? '公开' : '不公开');
        if(data.public){
            $("#owner_list_box").hide();
        }else{
            $("#owner_list_box").show();
        }
        $("#host_list").html(data.instances.join(', ') || '-');
    }
    // 初始化页面函数
    function init() {
        getSubnetAjax();
    }
    init();
});