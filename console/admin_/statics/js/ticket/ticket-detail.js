/**
 * Created by wuyang on 16/8/17.
 */
define(['utils'], function(utils) {
    $("#id-ticket-close-ticket").click(function() {
        $("#id-ticket-close-ticket-form").submit();
    });

    $("#id-send-ticket-to-me").click(function() {
        $("#ticket-send-ticket-to-me-form").submit();
    });

    $("#id-finish-ticket").click(function() {
        $("#ticket-finish-ticket-form").submit();
    });

    $("#id-process-ticket").click(function() {
        $("#ticket-process-ticket-form").submit();
    });

    $("#id-ticket-send-ticket").click(function() {
        $("#ticket-send-ticket-form").submit();
    });
});