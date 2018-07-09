/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    var id = location.search.match(/=(.*$)/)[1];
    utils._ajax({
        url: '/admin/physical_machine/baseinfo/api',
        data: {physical_machine_hostname: id},
        succCB: function(result) {
            var data = result.ret_set[0];
            var networkNum = 0;
            for (var i = 0, len = data.nic_info.length; i < len; i++) {
                networkNum += (+data.nic_info[i].num);
            }
            $('#networkNum').val(networkNum);

            $('#model').val(data.model);
            $('#drsStatus').val(data.drs ? '是' : '否');

            $('#cpuUsepro').html((100 - parseFloat(data.cpu_info.idle)).toFixed(2) + '%');
            $('#cpuUsebar').width(100 - data.cpu_info.idle + '%');

            $('#cpuScale').html((100 - parseFloat(data.cpu_info.idle)).toFixed(2) + '%');

            $('#memoryScale').html(utils.toMemory(data.mem_info.total - data.mem_info.available) + '/' + utils.toMemory(data.mem_info.total));

            $('#manage_ip').val(data.manage_ip);
            $('#ipmi_ip').val(data.ipmi_ip);
            $('#uname').val(data.uname);

            var memUsed = ((+data.mem_info.total) - (+data.mem_info.available)) / (+data.mem_info.total);

            if (!isNaN(memUsed) && isFinite(memUsed)) {
                $('#memoryUsebar').width(memUsed.toFixed(2) * 100 + '%');
                $('#memoryUsepro').html((memUsed * 100).toFixed(2) + '%');
            } else {
                $('#memoryUsebar').width('0%');
                $('#memoryUsepro').html('0%');
            }

        }
    });
    utils._ajax({
        url: '/admin/physical_machine/vm_amount/api',
        data: {physical_machine_hostname: id},
        succCB: function(data) {
            var vm_amount = data.ret_set.vm_amount;
            $('#vmNum').val(vm_amount);
        }
    });

    function getChartsData(labels) {
        utils._ajax({
            data: {
                resource_type: $('#SupervisorOption').val(),
                physical_machine_hostname: id,
                time_range: $('#SupervisorCycle').val()
            },
            url: '/admin/physical_machine/resourceusage/api',
            succCB: function(result) {
                $('#SupervisorCanvasDiv').empty();
                var canvasStr = '<canvas id="SupervisorCanvas" width="900" height="320"></canvas>';
                $('#SupervisorCanvasDiv').html(canvasStr);
                cxt = $('#SupervisorCanvasDiv').find('canvas')[0].getContext('2d');
                drawCharts(result.ret_set, labels);
                if ($('#SupervisorCycle').val() === 'real_time') {
                    setTimeout(function() {
                        getChartsData(returnLabels());
                    }, 5000);
                }
            }
        });
    }
    function drawCharts(data, labels) {
        var datasets = [];
        if (data instanceof Array) {
            datasets = [
                {
                    fill: false,
                    fillColor: "rgba(18,164,244,0.2)",
                    strokeColor: "rgba(18,164,244,1)",
                    pointColor: "rgba(18,164,244,1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(220,220,220,1)",
                    data: (function(data) {
                        return data.map(function(w) {
                            return w.toFixed(2);
                        });
                    })(data)
                }
            ];
        } else {
            datasets = [
                {
                    fill: false,
                    fillColor: "rgba(18,164,244,0.2)",
                    strokeColor: "rgba(18,164,244,1)",
                    pointColor: "rgba(18,164,244,1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(220,220,220,1)",
                    data: (function(data) {
                        return data.in_bytes.map(function(w) {
                            return (w / 1024 / 1024).toFixed(2);
                        });
                    })(data)
                }, {
                    fill: false,
                    fillColor: "rgba(220,220,220,0.5)",
                    strokeColor: "rgba(220,220,220,1)",
                    pointColor: "rgba(220,220,220,1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(151,187,205,1)",
                    data: (function(data) {
                        return data.out_bytes.map(function(w) {
                            return (w / 1024 / 1024).toFixed(2);
                        });
                    })(data)
                }
            ];
        }
        var _data = {
            labels: labels,
            datasets: datasets
        };
        if (datasets.length == 1) {
            new Chart(cxt).Line(_data, {
                bezierCurve: false,
                tooltipTemplate: "<%if (label){%><%=label%>  <%}%><%= value+'%' %>",
                scaleLabel: "<%=value%>%"
            });
        } else {
            new Chart(cxt).Line(_data, {
                bezierCurve: false,
                tooltipTemplate: "<%if (label){%><%=label%>  <%}%><%= value+'GB' %>",
                scaleLabel: "<%=value%>GB"
            });
        }

    }

    // 物理资源详情chart
    var cxt = document.getElementById("SupervisorCanvas").getContext('2d');

    function returnLabels() {
        var labels = [];
        var date = new Date().getTime();
        switch ($('#SupervisorCycle').val()) {
            case 'real_time':
                var step = 1;
                for (var i = 0; i < 60; i += 1) {
                    labels.push(utils.toDate(date));
                    date = date - step * 1000;
                }
                break;
            case 'six_hour':
                var step = 5;
                for (var i = 0; i < 72; i += 2) {
                    labels.push(utils.toDate(date));
                    date = date - step * 60 * 1000;
                }
                break;
            case 'one_day':
                var step = 15;
                for (var i = 0; i < 96; i += 2) {
                    labels.push(utils.toDate(date, 'MM-dd hh:mm'));
                    date = date - step * 60 * 1000;
                }
                break;
            case 'two_week':
                var step = 120;
                for (var i = 0; i < 168; i += 3) {
                    labels.push(utils.toDate(date, 'MM-dd hh:mm'));
                    date = date - step * 60 * 1000;
                }
                break;
            case 'one_month':
                var step = 480;
                for (var i = 0; i < 90; i += 2) {
                    labels.push(utils.toDate(date, 'yy-MM-dd hh:mm'));
                    date = date - step * 60 * 1000;
                }
                break;
        }
        return labels;
    }
    getChartsData(returnLabels());
    // 改变监控周期
    $('#SupervisorCycle,#SupervisorOption').on('change', function() {
        getChartsData(returnLabels());
    });
});