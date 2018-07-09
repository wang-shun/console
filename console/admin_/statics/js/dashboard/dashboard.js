/**
 * Created by wuyang on 16/8/4.
 */
define(['utils'], function(utils) {
    $("#id-config-dashboard").click(function() {
        $("#id-config-dashboard-modal").modal();

        $(".dashboard-config-item").click(function() {
            var _data = {};
            $(".dashboard-config-item").each(function(k, v) {
                _data[$(v).prop("name")] = {
                    show: $(v).prop("checked")
                };
            });

            var _id = "id-" + $(this).prop("name").split("_").join("-");

            if ($(this).prop("checked")) {
                $("#" + _id).removeClass("hidden");
            } else {
                $("#" + _id).addClass("hidden");
            }

            // Ajax提交表单数据
            utils._ajax({
                type: 'post',
                url: '/common/dashboard/config',
                data: _data,
            });
        });
    });
    $.get("/admin/resources/overview", {}, function(data) {
        var cpu_lv = 0, neicun_lv = 0, yingpan_used = 0, yingpan_total = 0;
        var arr = data.ret_set.resources;
        var usageChartArr = [];

        if (data.ret_code == "200" && arr) {
            for (var i = 0, len = arr.length; i < len; i++) {
                if (arr[i].id == "cpu") {
                    cpu_lv = ~~(arr[i].used / arr[i].total * 100);
                }
                if (arr[i].id == "memory") {
                    neicun_lv = ~~(arr[i].used / arr[i].total * 100);
                }

                if (arr[i].id == "disk_sata_cap" || arr[i].id == "disk_ssd_cap") {
                    yingpan_used += ~~arr[i].used;
                    yingpan_total += ~~arr[i].total;
                }
                if (
                    arr[i].id == "cpu" ||
                    arr[i].id == "memory" ||
                    arr[i].id == "disk_sata_cap" ||
                    arr[i].id == "disk_ssd_cap" ||
                    arr[i].id == "instance" ||
                    arr[i].id == "pri_nets" ||
                    arr[i].id == "pub_nets"
                ) {

                    // if (arr[i].id == "pri_nets") {
                    //     arr[i].name = '子网';
                    // }

                    usageChartArr.push({
                        usageText: arr[i].name + "<span>" + arr[i].used + "</span>" + "/" + "<span>" + arr[i].total + "</span>" + "(" + arr[i].unit + "):",
                        isHighlight: true,
                        usageData: {
                          used: arr[i].used,
                          total: arr[i].total
                        }
                    });
                }
            }
        }

        $("#resources_list").append(utils.usageChart(usageChartArr));

        yingpan_lv = ~~(yingpan_used / yingpan_total * 100);
        var used_color = '#f8e36f';
        var total_color = '#6ec8fb';
        var _data = [{
                value: yingpan_lv,
                label: "硬盘",
                color: used_color
            }, {
                value: 100 - yingpan_lv,
                label: "剩余",
                color: total_color
            }
        ];
        var ctx = $("#id-resources-map3").get(0).getContext("2d");
        $("#resources_tip3").html("硬盘使用率" + yingpan_lv + "%");
        new Chart(ctx).Pie(_data, {
            tooltipTemplate: "<%if (label){%><%=label%>: <%}%><%= value+'%' %>",
        });
        var _data2 = [
            {
                value: neicun_lv,
                label: "内存",
                color: used_color
            },
            {
                value: 100 - neicun_lv,
                label: "剩余",
                color: total_color
            }
        ];
        var ctx2 = $("#id-resources-map2").get(0).getContext("2d");
        $("#resources_tip2").html("内存使用率" + neicun_lv + "%");
        new Chart(ctx2).Pie(_data2, {
            tooltipTemplate: "<%if (label){%><%=label%>: <%}%><%= value+'%' %>",
        });
        var _data3 = [
            {
                value: cpu_lv,
                label: "CPU",
                color: used_color
            },
            {
                value: 100 - cpu_lv,
                label: "剩余",
                color: total_color
            }
        ];
        var ctx = $("#id-resources-map1").get(0).getContext("2d");
        $("#resources_tip1").html("CPU使用率" + cpu_lv + "%");
        new Chart(ctx).Pie(_data3, {
            tooltipTemplate: "<%if (label){%><%=label%>: <%}%><%= value+'%' %>",
        });
    });

});
