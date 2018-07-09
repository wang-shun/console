/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    $('#search').multiselect({
        search: {
            left: '<input type="text" name="q" class="form-control" placeholder="Search..." />',
            right: '<input type="text" name="q" class="form-control" placeholder="Search..." />'
        }
    });
});