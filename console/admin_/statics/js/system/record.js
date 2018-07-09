/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function (utils) {
    var owner = $('#owner').val();
    var zone = $("#zone").val();
    var _datatable = null;
    var loadDataTableIndex = 0;
    var config = {
        flavor: [],
        image: [],
        account: [],
        nets: []
    };
    var columns = [{
        "data": "record_user__nickname",
        "name": "nickname",
        "orderable": false
    }, {
        "data": "action_type",
        "name": "action_type"
    }, {
        "data": "detail",
        "name": "detail"
    }, {
        "data": "create_datetime",
        "name": "create_datetime"
    }];
    //用户
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
            var str = "";
            for (var i = 0, j = data.length; i < j; i++) {
                config['account'][data[i].id] = data[i].name;
            }
            loadDataTable();
        }
    });
    // 子网
    utils._ajax({
        url: "/console/api",
        data: {
            action: 'DescribeNets',
            owner: owner,
            zone: zone
        },
        finalCB: function (result) {
            var nets = result.ret_set;
            for (var i = 0, j = nets.length; i < j; i++) {
                config['nets'][nets[i].id] = nets[i].network_name;
            }
            loadDataTable();
        }
    });
    //镜像
    utils._ajax({
        url: "/console/api",
        data: {
            action: 'DescribeImages',
            owner: owner,
            zone: zone
        },
        finalCB: function (result) {
            var data = result.ret_set;
            for (var i = 0, j = data.length; i < j; i++) {
                config['image'][data[i].image_id] = data[i].image_name;
            }
            loadDataTable();
        }
    });
    //flavor
    utils._ajax({
        url: "/console/api",
        data: {
            action: 'ShowInstanceTypes',
            owner: owner,
            zone: zone
        },
        finalCB: function (result) {
            var data = result.ret_set;
            for (var i = 0, j = data.length; i < j; i++) {
                var flavor = data[i].vcpus + '核 ' + data[i].ram + 'G ' + data[i].disk + 'G ';
                config['flavor'][data[i].name] = flavor;
            }
            loadDataTable();
        }
    });
    function loadDataTable() {
        loadDataTableIndex++;
        if (loadDataTableIndex < 4) {
            return false;
        };
        var columnDefs = [{
            targets: 2,
            render: function (data, type, item) {
                var str = data;
                if (/^极速创建/.test(str)) {
                    str = str.replace(/创建:(.*)(?=\s\d+台)/, function($0,$1,$2){
                        return '创建：' + config['account'][$1];
                    }).replace(/台-(.*)(?=为用户)/, function($0,$1,$2){
                        return '台-<br>' + config['account'][$1];
                    }).replace(/为用户(.*)(?=创建)/, function($0,$1,$2){
                        return '为用户' + config['account'][$1] + '<br>';
                    }).replace(/配置(.*)(?=镜像)/, function($0,$1){
                        return '<br>配置为：' + config['flavor'][$1] + '<br>';
                    }).replace(/镜像(.*)(?=网络)/, function($0,$1){
                        return '镜像为：' + config['image'][$1] + '<br>';
                    }).replace(/网络(.*)(?=的主机)/, function($0,$1){
                        function mapNet(data) {
                            var reg = /u'id'\s*?:\s*?u'([^']+)'/g;
                            var ids = [];
                            var res = reg.exec(data);
                            while (res) {
                                ids.push(config['nets'][res[1]]);
                                res = reg.exec(data);
                            }
                            return ids.join(', ');
                        }
                        return '网络为：' + mapNet($1) + '<br>';
                    });
                }
                return str;
            }
        }];
        utils.datatable($("#id-action-record-list-table"), {
            columns: columns,
            columnDefs: columnDefs,
            order: [[3, 'desc']]
        }, '/admin/system_record/list/api');
    }

});