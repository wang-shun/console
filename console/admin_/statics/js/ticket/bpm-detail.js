/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    var id = location.search.match(/id=([^&]+)/)[1];
    var bpm_detail_table = [{
        name: 'id',
        text: 'ID'
    }, {
        name: 'user_id',
        text: '客户ID'
    }, {
        name: 'user_name',
        text: '客户姓名'
    }, {
        name: 'email',
        text: '邮箱账号'
    }, {
        name: 'created_at',
        text: '提交时间'
    }, {
        name: 'title',
        text: '申请标题'
    }, {
        name: 'resource_types',
        text: '申请类型'
    }, {
        name: 'resources',
        text: '申请数量'
    }, {
        name: 'status',
        text: '申请状态'
    }, {
        name: 'edited_users',
        text: '参与人'
    }, {
        name: 'log',
        text: '申请日志'
    }, {
        name: 'last_edited_by',
        text: '最后处理人'
    }, {
        name: 'created_at',
        text: '最后处理时间'
    }, {
        name: 'comment',
        text: '备注'
    }];
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
    utils._ajax({
        url: "/admin/audits/" + id,
        type: 'get',
        finalCB: function(data) {
            var audit = data.ret_set.audit;
            var bpm_table_body = '';
            bpm_detail_table.forEach(function(v) {
                var tmp_str = audit[v.name];
                if ('status' == v.name) {
                    tmp_str = status[tmp_str];
                } else if ('resource_types' == v.name) {
                    tmp_str = utils.arrToString(tmp_str, resources);
                } else if ('resources' == v.name) {
                    tmp_str = "";
                    audit[v.name].forEach(function(w) {
                        tmp_str += resources[w.type] + ':' + w.capacity + w.unit + '  ';
                    });
                }
                bpm_table_body += '<tr><td>' + v.text + ':</td><td>' + tmp_str + '</td></tr>';
            });
            $('#bpm_table_body').html(bpm_table_body);
            if (!/(approved_2|rejected_1|rejected_2|success)/.test(audit.status)) {
                $("#bpm_submit").removeProp('disabled');
                $("#bpm_esc").removeProp('disabled');
            }
            $("#bpm_submit").click(function() {
                bpm_click('pass');
            });
            $("#bpm_esc").click(function() {
                bpm_click('revoke');
            });
            function bpm_click(bpm_falg) {
                $.ajax({
                    url: '/admin/audits/' + id + '/change_status',
                    type: 'put',
                    data: {
                        audit_id: ~~id,
                        action: bpm_falg
                    },
                    success: function(data) {
                        if (bpm_falg == 'pass') {
                            alert('同意申请');
                        } else {
                            alert('拒绝申请');
                        }
                        location.href = '/admin/ticket/bpm';
                    },
                    error: function(err) {
                        console.log(err);
                    },
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", utils.getCookie("csrftoken"));
                    }
                });
            }
        }
    });
});


