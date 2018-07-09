/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    var columns = [{
            "data": "ip_pool_id",
            "name": "ip_pool_id"
        }, {
            "data": 'status',
            "name": 'status'
        }, {
            "data": "allocated_count",
            "name": "allocated_count"
        }, {
            "data": "line",
            "name": "line"
        }, {
            "data": "bandwidth",
            "name": "bandwidth"
        },
        {
             "data": "subnets",
             "name": "subnets"
        },
        {
            "data": "total_ips",
            "name": "total_ips"
}
    ];
    var columnDefs = [{
        targets: 0,
        render: function(data, type, row) {

            return '<a href="/admin/sourceManage/netDetail?netName=' + data + '">' + data + '</a>';
        }
    }, {
        targets: 1,
        render: function(data) {
            var json = {
                'available': '可使用'
            };
            return json[data] || '不可用';
        }
    }, {
        targets: 5,
        render: function(data, type, row) {
            var baseHtml = '';
            for (var i = 0; i < data.length; i++) {
                for (var j = 0; j < data[i].allocation_pools.length; j++) {
                    baseHtml += '<p>' + data[i].allocation_pools[j].start + '-' + data[i].allocation_pools[j].end + '</p>';
                }
            }
            return baseHtml;
        }
    }
    ];
    utils.datatable($("#netSourceTable"), {
        columns: columns,
        columnDefs: columnDefs,
        order: [[2, 'desc']]
    }, {url: '/admin/network/public_ip_pool/api', data: {'action': 'DescribePublicIPPoolList'}});
// 刷新
    $("#refresh").on("click", function() {
        location.reload();
    });
});