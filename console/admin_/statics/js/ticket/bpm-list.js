/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    var $bpm_table_list = $("#bpm_table_list");


    var status = {
        "pending": "审批中",
        "approved_1": "管理员审批通过",
        "approved_2": "超级管理员审批通过",
        "rejected_1": "审批驳回",
        "rejected_2": "超级管理员审批驳回",
        "success": "资源已建立"
    };
    var resources = {
        'disk_num': '磁盘个数',
        'disk_sata_cap': 'SATA磁盘大小',
        'disk_ssd_cap': 'SSD磁盘大小',
        'memory': '内存',
        'cpu': 'CPU',
        'instance': '主机',
        'bandwidth': '带宽',
        'pub_nets': '公网子网',
        'pri_nets': '内网子网',
        'keypair': '密钥',
        'router': '路由器',
        'pub_ip': '公网IP',
        'security_group': '安全组',
        'backup': '备份',
    };
    var columns = [
        {"data": "id", 'name': 'id'},
        {"data": "user_id", 'name': 'user_id'},
        {"data": "create_datetime", 'name': 'create_datetime'},
        {"data": "title", 'name': 'title'},
        {
            "data": "status",
            'name': 'status',
            "render": function(data) {
                return status[data];
            }
        },
        {"data": "last_edited_at", 'name': 'last_edited_at'}
    ];
    var columnDefs = [{
        targets: 0,
        render: function(data, type, row, meta) {
            return '<a href=\"javascript:location.href=\'\/admin\/ticket\/bpm_detail?id=' + row.id + '\'\">' + row.id + '</a>';
        }
    }];

    var json = {};
    // 获取一系列条件
    var $user_id = $('#user_id');
    var $user_name = $('#user_name');
    var $edited_user_name = $('#edited_user_name');
    var $title = $('#title');
    var $started_at = $('#started_at');
    var $ended_at = $('#ended_at');

    $("#bpm_search").click(function() {
        $user_id.val() && (json.user_id = $user_id.val());
        $user_name.val() && (json.user_name = $user_name.val());
        $edited_user_name.val() && (json.edited_user_name = $edited_user_name.val());
        $title.val() && (json.title = $title.val());
        $started_at.val() && (json.started_at = parseInt(new Date($started_at.val()).getTime() / 1000));
        $ended_at.val() && (json.ended_at = parseInt(new Date($ended_at.val()).getTime() / 1000));
        reset_bpm_table();
    });
    $("#bpm_reset").click(function() {
        $user_id.val('');
        $user_name.val('');
        $edited_user_name.val('');
        $title.val('');
        $started_at.val('');
        $ended_at.val('');
        json = undefined;
        reset_bpm_table();
    });

    function reset_bpm_table() {
        $bpm_table_list.dataTable().fnDestroy();
        $bpm_table_list.find('thead').html('<tr><th>ID</th>\
                    <th>客户ID</th>\
                    <th>提交时间</th>\
                    <th>申请标题</th>\
                    <th>状态</th>\
                    <th>最后处理时间</th>');
        $bpm_table_list.find('tbody').empty();
        creat_bpm_talbe(json);
    }
    creat_bpm_talbe();
    function creat_bpm_talbe(data) {
        utils.datatable($bpm_table_list, {columns: columns, order: [[2, 'desc']], columnDefs: columnDefs}, {url: '/admin/audits', data: data});
    }
});
