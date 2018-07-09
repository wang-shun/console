/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    var columns = [{
            "data": "gid",
            "name": "group_id"
        }, {
            "data": "name",
            "name": "group_name"
        }, {
            "data": "creator__account__nickname",
            "name": "group_creator"
        }, {
            "data": "created_at",
            "name": "create_datetime"
        }
    ];
    var columnDefs = [{
        targets: 0,
        render: function(data) {
            return data;
        }
    }];
    var _datatable = utils.datatable($("#id-perm-group-list-table"), {
        columns: columns,
        columnDefs: columnDefs,
        order: [[3, 'desc']]
    }, '/admin/perm_group/list/api');

    utils.tableClick($("#id-perm-group-list-table").find('tbody'), {
        callback: function(obj) {
            $("#id-delete-perm-group").prop("disabled", !$(obj).hasClass("selected"));
        }
    });
    $("#id-create-perm-group").click(function() {
        $("#id-create-perm-group-modal").modal();
        $("#id-create-perm-group-submit-btn").prop("disabled", false);
        $("#id-create-perm-group-form").find("input[name='group_name']").val("");
    });
    $("#id-create-perm-group-submit-btn").on("click", function() {
        var group_name = $("#id-create-perm-group-form").find("input[name='group_name']").val();
        if (!group_name) {
            utils.errMsg("请输入权限组名称");
            return;
        }
        utils._ajax({
            url: "/admin/system/perm_group/create",
            data: {"name": group_name},
            succCB: function() {
                utils.succMsg("创建权限组成功");
                $("#id-create-perm-group-modal").modal("hide");
                _datatable.ajax.reload();
            },
            errCB: function() {
                utils.errMsg("创建权限组失败");
                $("#id-create-perm-group-modal").modal("hide");
            },
            error: function() {
                utils.errMsg("创建权限组失败");
                $("#id-create-perm-group-modal").modal("hide");
            }
        });
    });
    $("#id-delete-perm-group").on("click", function() {
        $("#id-delete-perm-group-modal").modal();
    });
    $("#id-delete-perm-group-submit-btn").click(function() {
        var _selected_row = _datatable.row('.selected').node();
        var _group_id = $(_selected_row).children('td:eq(0)').text();
        utils._ajax({
            url: "/admin/system/perm_group/delete",
            data: {"group_id": _group_id},
            succCB: function() {
                utils.succMsg("删除权限组成功");
                $("#id-delete-perm-group-modal").modal("hide");
                _selected_row.remove();
                _datatable.ajax.reload();
                $("#id-delete-perm-group").prop("disabled", true);
            },
            errCB: function() {
                utils.errMsg("删除权限组失败");
                $("#id-delete-perm-group-modal").modal("hide");
            },
            error: function() {
                utils.errMsg("删除权限组失败");
                $("#id-delete-perm-group-modal").modal("hide");
            }
        });
    });

});
