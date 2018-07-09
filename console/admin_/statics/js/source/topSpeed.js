define(['utils'], function(utils) {
    var owner = $('#owner').val();
    var zone = $("#zone").val();
    var _datatable = null;
    var security_groups = "";
    var public_nets = [];
    var private_nets = [];
    var resource_pool_name = {};
    var resource_pool_list = [];
    var config = {
        flavor: [],
        image: [],
        account: [],
        nets: [],
        pool: []
    };
    $("#createTopSpeed").on("click", function() {
        $("#createTopSpeedModal").modal();
    });
    var columns = [{
        data: "user",
        name: "user"
    }, {
        data: "instance_type_id",
        name: "instance_type_id"
    }, {
        data: "image_id",
        name: "image_id"
    }, {
        data: "nets",
        name: "nets"
    }, {
        data: "resource_pool_name",
        name: "resource_pool_name"
    }, {
        data: "remain_count",
        name: "remain_count"
    }];
    var columnDefs = [{
        targets: 0,
        render: function(data) {
            return config['account'][data] || data;
        }
    }, {
        targets: 1,
        render: function(data) {
            return config['flavor'][data] || data;
        }
    }, {
        targets: 2,
        render: function(data) {
            return config['image'][data] || data;
        }
    }, {
        targets: 3,
        render: function(data) {
            var reg = /u'id'\s*?:\s*?u'([^']+)'/g;
            var ids = [];
            var res = reg.exec(data);
            while (res) {
                ids.push(config['nets'][res[1]]);
                res = reg.exec(data);
            }
            return ids;
        }
    }];

    function loadDataTable() {
        $("#image").change(function() {
            var platform = $(this).find('option:selected').attr('platform');
            $("#flavor").find('option').removeAttr('selected');
            if (platform == 'windows') {
                $("#flavor").find('.linux-class').hide();
                $("#flavor").find('.all-class').eq(0).attr('selected', true);
            } else {
                $("#flavor").find('.linux-class').show();
                $("#flavor").find('option').eq(0).attr('selected', true);
            }
        });
        _datatable = utils.datatable($("#topSpeedTable"), {
            columns: columns,
            columnDefs: columnDefs
        }, {url: '/admin/pools/compute_resource/descr_top_speed'});
    }

    function getComputeResource(){
        // 资源池
        return new Promise(function(resolve,reject){
            utils._ajax({
                url: "/admin/pools/compute_resource/list",
                data: {
                    action: 'DescribeResourceOfcompute',
                    owner: owner,
                    zone: zone,
                    VM_type: 'KVM',
                    flag: 0,
                    length: 1,
                    start: 0
                },
                finalCB: function(result) {
                    var str = "";
                    var data = result.data;
                    for (var i = 0, j = data.length; i < j; i++) {
                        str += `<option value=${data[i].name} type=${data[i].type} name=${data[i].name}>${data[i].name}</option>`
                    }
                    resource_pool_list = data;
                    $("#pool").html(str);
                    resource_pool_name = Object.assign({},data[0]);
                    resolve(data[0].type);
                }
            });
        })
    }

    function getMember(type){
        // 用户
        return new Promise(function(resolve,reject){
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
                succCB: function(result) {
                    var data = result.ret_set.member_list;
                    var str = "";
                    for (var i = 0, j = data.length; i < j; i++) {
                        config['account'][data[i].id] = data[i].name;
                        str += "<option value=" + data[i].id + ">" + data[i].name + "</option>";
                    }
                    $("#select_user").html(str);
                    resolve();
                },
                errCB: function() {
                    reject();
                },
                error: function() {
                    reject();
                }
            });
        });
    }

    function getNets(type){
        // 子网
        return new Promise(function(resolve,reject){
            utils._ajax({
                url: "/console/api",
                data: {
                    action: 'DescribeNets',
                    owner: owner,
                    zone: zone,
                    subnet_type:type
                },
                succCB: function(result) {
                    var private_str = "";
                    var public_str = "";
                    var nets = result.ret_set;
                    public_nets = [];
                    private_nets = [];
                    for (var i = 0, j = nets.length; i < j; i++) {
                        config['nets'][nets[i].id] = nets[i].name;
                        if (nets[i].gateway_ip) {
                            public_nets.push(nets[i]);
                        } else {
                            private_nets.push(nets[i]);
                        }
                    }
                    for (var i = 0, j = private_nets.length; i < j; i++) {
                        private_str += "<div class='checkbox'><label><input type='checkbox' name='nets' value='" + private_nets[i].id + "|" + private_nets[i].network_id + "'>" + private_nets[i].name + "</label></div>";
                    }
                    for (var i = 0, j = public_nets.length; i < j; i++) {
                        public_str += "<option value='" + public_nets[i].id + "|" + public_nets[i].network_id + "'>" + public_nets[i].name + "</option>";
                    }
                    $("#net_list").html(private_str);
                    $("#public_nets").html(public_str);
                    resolve();
                },
                errCB: function() {
                    reject();
                },
                error: function() {
                    reject();
                }
            });
        });
    }

    function getImages(type){
        // 镜像
        return new Promise(function(resolve,reject){
            utils._ajax({
                url: "/console/api",
                data: {
                    action: 'DescribeImages',
                    owner: owner,
                    zone: zone,
                    hypervisor_type: type
                },
                succCB: function(result) {
                    var str = "";
                    var data = result.ret_set;
                    for (var i = 0, j = data.length; i < j; i++) {
                        config['image'][data[i].image_id] = data[i].image_name;
                        str += "<option value=" + data[i].image_id + " platform=" + data[i].platform + ">" + data[i].image_name + "</option>";
                    }
                    $("#image").html(str);
                    resolve();
                },
                errCB: function() {
                    reject();
                },
                error: function() {
                    reject();
                }
            });
        });
    }

    function getTypes(type){
        // flavor
        return new Promise(function(resolve,reject){
            utils._ajax({
                url: "/console/api",
                data: {
                    action: 'ShowInstanceTypes',
                    owner: owner,
                    zone: zone,
                    flavor_type: type
                },
                succCB: function(result) {
                    var str = "";
                    var data = result.ret_set;
                    for (var i = 0, j = data.length; i < j; i++) {
                        var flavor = data[i].vcpus + '核 ' + data[i].ram + 'G ' + data[i].disk + 'G ';
                        config['flavor'][data[i].name] = flavor;
                        str += "<option value=" + data[i].name + " disk=" + data[i].disk + " class=" + ((data[i].disk < 40) ? 'linux-class' : 'all-class') + ">" + flavor + "</option>";
                    }
                    $("#flavor").html(str);
                    resolve();
                },
                errCB: function() {
                    reject();
                },
                error: function() {
                    reject();
                }
            });
        });
    }

    function getGroup(type){
        // 默认安全组
        return new Promise(function(resolve,reject){
            utils._ajax({
                url: "/console/api",
                data: {
                    action: 'DescribeSecurityGroup',
                    owner: owner,
                    zone: zone,
                },
                succCB: function(result) {
                    var data = result.ret_set;
                    security_groups = data[0].sg_id;
                    resolve();
                },
                errCB: function() {
                    reject();
                },
                error: function() {
                    reject();
                }
            });
        });
    }

    function setValue(){
        return function(value){
            return Promise.all([getMember(value), getNets(value), getImages(value), getTypes(value), getGroup(value)])
        }
    }

    Promise.resolve(getComputeResource()).then(setValue()).then(loadDataTable).catch(function(error){
        loadDataTable();
    });

    $("#pool").change(function(){
        var data = resource_pool_list.filter((item) => {
            return item.name === $(this).val()
        });
        resource_pool_name = data[0];
        Promise.resolve(resource_pool_name.type).then(setValue());
    });

    $("#createTopSpeedModalBtn").click(function() {
        var nets = [];
        $("#net_list").find("input[name=nets]:checked").each(function() {
            var val = $(this).val().split('|');
            nets.push(
                {
                    id: val[0],
                    network_id: val[1]
                }
            );
        });
        if ($("#public_nets").val()) {
            var val = $("#public_nets").val().split('|');
            nets.push(
                {
                    id: val[0],
                    network_id: val[1]
                }
            );
        }
        var count = parseInt($("#count").val());
        if (isNaN(count)) {
            utils.errMsg('请输入正确的数量');
            return false;
        }
        var params = {
            action: "RunInstances",
            user: $("#select_user").val(),
            owner: owner,
            zone: zone,
            instance_name: '极速创建',
            image_id: $("#image").val(),
            instance_type_id: $("#flavor").val(),
            disks: [],
            nets: nets,
            use_basenet: true,
            security_groups: [security_groups],
            login_mode: 'PWD',
            login_keypair: "",
            login_password: $("#password").val(),
            count: count,
            package_size: 0,
            charge_mode: 'pay_on_time',
            resource_pool_name: resource_pool_name.name,
            VM_type: resource_pool_name.type
        };

        utils._ajax({
            url: "/admin/pools/compute_resource/top_speed_admin",
            contentType: 'application/json',
            data: JSON.stringify(params),
            succCB: function() {
                $('#createTopSpeedModal').modal('hide');
                utils.succMsg("创建成功");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            },
            errCB: function() {
                utils.errMsg("创建失败");
            },
            error: function() {
                utils.errMsg("创建失败");
            }
        });
    });
});
