define(['utils'], function(utils) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var param = utils.getUrlParams();

    utils._ajax({
        url: "/admin/pools/compute_resource/list_one_pool",
        contentType: 'application/json',
        data: JSON.stringify({
          owner: $("#owner").val(),
          zone: $("#zone").val(),
          name: decodeURIComponent(param.name),
        }),
        succCB: function(result) {
            var data = result.ret_set[0];

            $("#name").html(data.name);
            $("#host_count").html(data.host_count);
            $("#cpu").html(getFixed(data.cpu));
            $("#memory").html(getFixed(data.memory.use_mem / data.memory.total_mem));
            $("#instances_count").html(data.instances_count);
            $("#hosts").html(data.hosts.map(function(item) {
                return '<a href="/admin/sourceManage/physicsSource?name=' + item + '">' + item + '</a></br>';
            }));
        },
        errCB: function(err) {
          utils.errMsg(err.ret_msg);
        },
        error: function() {
        }
    });
    function getFixed(num) {
        num = num * 100;
        if (isNaN(num)) {
            return '0.00%';
        }
        return num.toFixed(2) + '%';
    }
});