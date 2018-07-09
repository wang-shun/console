/**
 * Created by wuyang on 16/8/4.
 */

define(function() {

    var DATATABLE_LANGUAGE_OPTION = {
        processing: "正在加载数据...",
        search: "搜索",
        lengthMenu: "每页 _MENU_ 个",
        info: "显示 _TOTAL_条 中 _START_ 到 _END_ 条的记录",
        infoEmpty: "",
        infoFiltered: "（从 _MAX_ 条总记录中过滤的结果）",
        loadingRecords: "正在加载...",
        zeroRecords: "没有找到记录",
        emptyTable: "没有找到记录",
        paginate: {
            first: "第一页",
            previous: "上一页",
            next: "下一页",
            last: "最后一页"
        },
        aria: {
            sortAscending: ": 顺序",
            sortDescending: ": 倒序"
        }
    };
    var DATATABLE_SCROLLY = "360px";

    return {
        DATATABLE_LANGUAGE_OPTION: DATATABLE_LANGUAGE_OPTION,
        DATATABLE_SCROLLY: DATATABLE_SCROLLY
    };

});


