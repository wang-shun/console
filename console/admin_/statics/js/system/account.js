/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {

    var $table = $("#id-system-account-list-table");
    var _datatable = null;
    var columns = [{
            "data": "user__username",
            "name": "username"
        }, {
            "data": "type",
            "name": "type"
        }, {
            "data": "name",
            "name": "name"
        }, {
            "data": "email",
            "name": "email"
        }, {
            "data": "telephone",
            "name": "telephone"
        }, {
            "data": "user_group",
            "name": "user_group"
        }, {
            "data": "last_logined_at",
            "name": "last_logined_at",
            "searchable": false
        }, {
            "data": "created_at",
            "name": "created_at",
            "searchable": false
        }
    ];
    var columnDefs = [{
        targets: 5,
        render: function(data, type, row, meta) {
            if (data.length) {
                return data[0].name;
            } else {
                return '未分组';
            }
        },
    }];
    reload_account_table();
    $("#refresh").click(function() {
      location.reload();
    });
    $("#id-create-system-account").on("click", function() {
        $("#id-create-system-account-modal").modal();
    });
    $("#id-create-system-account-submit-btn").click(function() {
        var email = $("#id-create-system-account-form").find("input[name='email']").val();
        var password = $("#id-create-system-account-form").find("input[name='password']").val();
        var type = $("#id-create-system-account-form").find("select[name='type']").val();
        var telephone = $("#id-create-system-account-form").find("input[name='telephone']").val();
        var group_id = $("#select_user_group").val();
        var _data = {
            "email": email,
            "type": type,
            "password": password,
            "telephone": telephone,
        };
        if (group_id !== 'none') {
            _data.group_id = group_id;
        } else {
            delete _data.group_id;
        }
        utils._ajax({
            url: "/admin/system/account/create",
            data: _data,
            succCB: function() {
                utils.succMsg("新增账号成功");
                $("#id-create-system-account-modal").modal("hide");
                _datatable.ajax.reload();
            },
            errCB: function() {
                utils.errMsg("新增账号失败");
                $("#id-create-system-account-modal").modal("hide");
            },
            error: function() {
                utils.errMsg("新增账号失败");
                $("#id-create-system-account-modal").modal("hide");
            }
        });
    });

    $("#id-edit-system-account").click(function() {
        var account_id = _datatable.$("tr.selected").children('td:eq(0)').html().match(/[^>]+(?=(?:\<|$))/g)[0];
        console.log(account_id);
        var perm_group_name = _datatable.$("tr.selected").children("td:eq(1)").html();
        var perm_group_id = "";
        $("#id-edit-system-account-form").find("input[name='account_id']").val(account_id);
        console.log($("#id-edit-system-account-form").find("input[name='account_id']"));
        $.get("/admin/common/perm_group/list", function(data) {
            var select_option = "<option value=''>--------------------</option>";
            $.each(data, function(k, v) {
                select_option += "<option value=" + v.gid + ">" + v.name + "</option>";
                if (v.name == perm_group_name) {
                    perm_group_id = v.gid;
                }
            });
            $("#id-edit-system-account-form").find("select[name='perm_group_id']").html(select_option).val(perm_group_id);
        }.bind(this));

        // 编辑系统用户对话框
        $("#id-edit-system-account-modal").modal();
        // 初始化弹出对话框
        $("#id-create-perm-group-submit-btn").prop("disabled", false);
    });

    $("#id-edit-system-account-submit-btn").on("click", function() {
        var account_id = $("#id-edit-system-account-form").find("input[name='account_id']").val();
        var perm_group_id = $("#id-edit-system-account-form").find("select[name='perm_group_id']").val();
        var _data = {
            "account_id": account_id,
            "name": name,
            "perm_group_id": perm_group_id
        };
        // Ajax提交表单数据
        utils._ajax({
            url: '/admin/system/account/edit',
            data: _data,
            succCB: function() {
                utils.succMsg("修改账号成功");
                _datatable.ajax.reload();
                $("#id-edit-system-account-modal").modal("hide");
                _datatable.ajax.reload();
            },
            errCB: function() {
                utils.errMsg("修改账号失败");
                $("#id-edit-system-account-modal").modal("hide");
            },
            error: function() {
                utils.errMsg("修改账号失败");
                $("#id-edit-system-account-modal").modal("hide");
            }
        });
    });

    $("#id-delete-system-account").click(function() {
        var account_id = _datatable.$("tr.selected").children('td:eq(0)').html();
        $("#id-edit-system-account-form").find("input[name='account_id']").val(account_id);
        // 编辑系统用户对话框
        $("#id-delete-system-account-modal").modal();
    });

    // Submit The Form
    $("#id-delete-system-account-submit-btn").on("click", function() {
        var account_id = $("#id-edit-system-account-form").find("input[name='account_id']").val();
        // Ajax提交表单数据
        utils._ajax({
            url: '/admin/system/account/delete',
            data: {"account_id": account_id.match(/[^>]+(?=(?:\<|$))/g)[0]},
            succCB: function() {
                utils.succMsg("删除账号成功");
                _datatable.ajax.reload();
                $("#id-delete-system-account-modal").modal("hide");
                _datatable.ajax.reload();
            },
            errCB: function() {
                utils.errMsg("删除账号失败");
                $("#id-delete-system-account-modal").modal("hide");
            },
            error: function() {
                utils.errMsg("删除账号失败");
                $("#id-delete-system-account-modal").modal("hide");
            }
        });
    });
    $("#id-password-system-account").click(function() {
        var account_id = _datatable.$("tr.selected").children('td:eq(0)').html();
        $("#id-edit-password-system-account-form").find("input[name='account_id']").val(account_id);
        // 修改密码对话框
        $("#id-password-system-account-modal").modal();
    });
    $("#id-password-system-account-submit-btn").click(function() {
        var account_id = _datatable.$("tr.selected").children('td:eq(0)').html();
        var $asp = $("#account_super_password");
        var $apn = $("#account_password_new");
        var $apc = $("#account_password_confirm");
        utils._ajax({
            url: '/admin/system/account/resetUserPassword',
            data: {
                "username": account_id,
                "admin_password": $asp.val(),
                "new_password": $apn.val(),
                "confirm_password": $apc.val()
            },
            succCB: function() {
                utils.succMsg("修改密码成功");
                $("#id-password-system-account-modal").modal("hide");
            },
            errCB: function(res) {
                utils.errMsg(res.ret_msg);
                $("#id-password-system-account-modal").modal("hide");
            },
            error: function(res) {
                utils.errMsg(res.ret_msg);
                $("#id-password-system-account-modal").modal("hide");
            }
        });

    });

   // 获取用户组

    function update_user_group(res) {
        var group = res.ret_set;
        var str = '';
        var selectStr = '';
        for (var i = 0; i < group.length; i++) {
            str += '<li role="presentation">' +
                '<a role="menuitem" groupid="' + group[i].id + '" tabindex="-1" class="user-group" href="#">' +
                     group[i].name +
                '</a>' +
            '</li>';
            selectStr += '<option value="' + group[i].id + '">' + group[i].name + '</option>';
        }
        $('#user_group').html($('#user_group').html() + str);
        $('#select_user_group').html($('#select_user_group').html() + selectStr);
    }

    utils._ajax({
        url: '/admin/api/',
        data: {
            'action': 'DescribeAccountUserGroup',
            'owner': $('#owner').val(),
            'zone': $('#zone').val()
        },
        succCB: function(res) {
            update_user_group(res);
        },
        errCB: function(res) {
            utils.errMsg(res.ret_msg);
        },
        error: function(res) {
            utils.errMsg(res.ret_msg);
        }
    });
    $("#user_group").on('click', '#add_user_group', function() {
        // 添加用户组
        $("#id-user-group-modal").modal();
    });

    $("#id-user-group-submit-btn").click(function() {
        var val = $("#id-user-group-input").val().trim();
        utils._ajax({
            url: '/admin/api/',
            data: {
                'action': 'CreateAccountUserGroup',
                'name': val,
                'owner': $('#owner').val(),
                'zone': $('#zone').val()
            },
            succCB: function(res) {
                utils.succMsg('用户名创建成功');
                update_user_group(res);
                $("#id-user-group-modal").modal("hide");
            },
            errCB: function(res) {
                utils.errMsg(res.ret_msg);
                $("#id-user-group-modal").modal("hide");
            },
            error: function(res) {
                utils.errMsg(res.ret_msg);
                $("#id-user-group-modal").modal("hide");
            }
        });
    });

    $("#user_group").on('click', '.user-group', function() {
        var groupid = $(this).attr('groupid');
        var param = {};
        if (groupid !== 'all') {
            if (groupid !== 'un_group') {
                param.group_id = groupid;
            } else {
                delete param.group_id;
            }

            create_account_table(param);
        } else {
            reload_account_table();
        }
        $("#selected-user-group").html($(this).html());
    });

    function reload_account_table() {
        $table.dataTable().fnDestroy();
        $table.find('tbody').empty();
        _datatable = utils.datatable($table, {
            columns: columns,
            columnDefs: columnDefs,
            order: [[7, 'desc']]
        }, '/admin/system_account/list/api');

        account_table_click();
    }

    function create_account_table(data) {
        $table.dataTable().fnDestroy();
        $table.find('tbody').empty();
        _datatable = utils.datatable($table, {
            columns: columns,
            columnDefs: columnDefs,
            order: [[7, 'desc']]
        }, {url: '/admin/system_account/user_group/api', data: data});

        account_table_click();
    }

    function account_table_click() {
        utils.tableClick($table.find('tbody'), {
            callback: function(obj) {
                _datatable.row(obj).data();
                $("#id-edit-system-account")
                    .add("#id-delete-system-account")
                    .add("#id-password-system-account").prop("disabled", !$(obj).hasClass("selected"));
            }
        });
    }
});
