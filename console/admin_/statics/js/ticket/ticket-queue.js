/**
 * Created by wuyang on 16/8/4.
 */
define(['utils'], function(utils) {
    var BASE_URL = $("input[name='base_url']").val();

    $(".ticket-queue-tab").click(function() {
        location.href = window.location.pathname + "?queue=" + $(this).prop("name");
    });

    $(".ticket-queue-page-size").add($(".ticket-queue-page")).change(function() {
        $(this).parent().parent().find(".ticket-queue-filter").change();
    });

    // 新工单计时
    var timing_new_ticket = function() {
        $("#new-ticket-table").find(".create-datetime").each(function(k, v) {
            $(v).next("span").text(utils.dateBetween(new Date($(v).val()), new Date()));
        });
    };

    var timing_processing_ticket = function() {
        $("#processing-ticket-table").find(".start-datetime").each(function(k, v) {
            $(v).next("span").text(utils.dateBetween(new Date($(v).val()), new Date()));
        });
    };

    var timing_pending_ticket = function() {
        $("#pending-ticket-table").find(".start-datetime").each(function(k, v) {
            $(v).next("span").text(utils.dateBetween(new Date($(v).val()), new Date()));
        });
    };

    setInterval(function() {
        timing_new_ticket();
        timing_processing_ticket();
        timing_pending_ticket();
    }, 1000);


    $(".send-new-ticket").click(function() {
        var ticket_id = $(this).parent().parent().find("input[name='ticket_id']").val();
        var post_url = BASE_URL + "/admin/ticket/detail/" + ticket_id;
        var send_ticket_form = $("#ticket-send-ticket-form");
        send_ticket_form.prop("action", post_url);
        send_ticket_form.find("input[name='ticket_id']").val(ticket_id);
    });


    $("#id-ticket-send-ticket").click(function() {
        $("#ticket-send-ticket-form").submit();
    });
});