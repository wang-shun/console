/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    var columns = [{
            "data": "ticket_id",
            "name": "ticket_id"
        }, {
            "data": "submit_user__user__username",
            "name": "username"
        }, {
            "data": "create_datetime",
            "name": "create_datetime",
            "searchable": "special"
        }, {
            "data": "subject",
            "name": "subject"
        }, {
            "data": "status",
            "name": "status",
            "searchable": "special",
            "orderable": "special"
        }, {
            "data": "ticket_type",
            "name": "ticket_type",
            "searchable": "special",
            "orderable": "special"
        }, {
            "data": "last_edit_user__nickname",
            "name": "last_edit_user"
        }, {
            "data": "last_edit_datetime",
            "name": "last_edit_datetime",
            "searchable": "special"
    }];
    utils.datatable($("#id-ticket-table"), {columns: columns, order: [[2, 'desc']]}, '/admin/ticket/list/api');
});