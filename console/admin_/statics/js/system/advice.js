/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    var columns = [
        {
            "data": "id",
            "name": "id"
        },
        {
            "data": "cell_phone",
            "name": "cell_phone"
        },
        {
            "data": "content",
            "name": "content"
        },
        {
            "data": "create_datetime",
            "name": "create_datetime"
        }
    ];
    utils.datatable($("#id-advice-list-table"), {
        columns: columns,
        order: [[3, 'desc']]
    }, '/admin/advice/list/api');
});