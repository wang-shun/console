/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    utils._ajax({
        url: '/admin/pools/storage_resource/list',
        finalCB: function(result) {
            var usageChartArr = [];
            var str = "";
            if (result.data.length == 0) {
                return false;
            }
            result.data.map(function(w) {
                var data = [{
                  usageText: '容量：' + utils.toMemory(w.volume.used, 'GB', 'GB', 0) + '/' + utils.toMemory(w.volume.total, 'GB', 'GB', 0),
                  isHighlight: true,
                  usageData: {
                    used: w.volume.used,
                    total: w.volume.total
                  }
                }, {
                  usageText: "类型：" + w.type,
                  isHighlight: false,
                  usageData: {}
                }, {
                  usageText: "状态：" + w.status,
                  isHighlight: false,
                  usageData: {}
                }];
                var id = "#storage_resource_" + w.name;
                usageChartArr.push({id: id, data: data});
                str += '<div class="panel">' +
                    '<div class="panel-heading dashboard-box-heading">' +
                        '<h4>' + w.name + '</h4>' +
                    '</div>' +
                    '<div class="panel-body">' +
                        '<div class="compute-resource-name"><b>硬盘（个）' + w.dev_num + '</b></div>' +
                        '<div id="storage_resource_' + w.name + '"></div>' +
                    '</div>' +
                '</div>';
            });
            $('#storage_resource').html(str);
            for (var i = 0; i < usageChartArr.length; i++) {
                $(usageChartArr[i].id).append(utils.usageChart(usageChartArr[i].data));
            }
        }
    });
    $(".page-title").hide();
    utils._ajax({
        url: '/admin/pools/compute_resource/list',
        data:{
            owner: $("#owner").val(),
            zone: $("#zone").val(),
            start: 0,
            length: 1,
        },
        finalCB: function(result) {
            var str = "";
            var usageChartArr = [];
            if (result.data.length == 0) {
                return false;
            }
            result.data.map(function(w) {
                var data = [{
                  usageText: '内存：' + utils.toMemory(w.memory.use_mem) + '/' + utils.toMemory(w.memory.total_mem),
                  isHighlight: true,
                  usageData: {
                    used: w.memory.use_mem,
                    total: w.memory.total_mem
                  }
                }, {
                  usageText: "CPU：" + (w.cpu * 100).toFixed(2) + "%",
                  isHighlight: true,
                  usageData: {
                    used: w.cpu * 100,
                    total: 100
                  }
                }];
                var id = "#compute_resource_" + w.name;
                usageChartArr.push({id: id, data: data});
                str += '<div class="panel">' +
                    '<div class="panel-heading dashboard-box-heading">' +
                        '<h4>' + w.name + '</h4>' +
                    '</div>' +
                    '<div class="panel-body">' +
                        '<div class="compute-resource-name"><b>宿主机（个）' + w.host_count + '</b></div>' +
                        '<div id="compute_resource_' + w.name + '"></div>' +
                    '</div>' +
                '</div>';
            });
            $('#compute_resource').html(str);
            for (var i = 0; i < usageChartArr.length; i++) {
                $(usageChartArr[i].id).append(utils.usageChart(usageChartArr[i].data));
            }
        }
    });

});
