/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    var id = location.search.match(/=(.*$)/)[1];
    var columns = [{
            "data": "ip_addr",
            "name": "ip_addr",
            "searchable": "special"
        }, {
            "data": "ip_status",
            "name": "ip_status"
        }, {
            "data": "binding_resource",
            "name": "binding_resource",
            "searchable": "special",
            "orderable": "special"
        }, {
            "data": "bandwidth",
            "name": "bandwidth"
        }
    ];
    var columnDefs = [{
        targets: 1,
        render: function(data) {
            var json = {
                'ACTIVE': '已绑定',
                'DOWN': '已分配'
            };
            return json[data] || "";
        }
    }, {
        targets: 2,
        render: function(data) {

            return JSON.parse(data).instance_id || "";
        }
    }];
    utils.datatable($("#outServerTable"), {
        columns: columns,
        columnDefs: columnDefs,
        order: [[2, 'desc']]
    }, {
            url: '/admin/network/public_ip_pool_detail/api',
            data: {
                'subnet_name': decodeURIComponent(id),
                'owner': $("#owner").val(),
                'zone': $('#zone').val()
            }
        }
    );
});
