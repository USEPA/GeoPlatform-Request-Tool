(function ($) {

    $(document).ready(function () {
        // skip on initial load
        let skip = {role: true, portal: true, user_type: true};
        $(':input[name$=role]').on('change', function () {
            if (!skip.role) {
                $(':input[name=authoritative_group]').val(null).trigger('change');
            } else {
                skip.role = false;
            }
        });
        $(':input[name$=user_type]').on('change', function () {
            if (!skip.user_type) {
                $(':input[name=role]').val(null).trigger('change');
            } else {
                skip.user_type = false;
            }
        });
        $(':input[name$=portal]').on('change', function () {
            if (!skip.portal) {
                $(':input[name=requester]').val(null).trigger('change');
                $(':input[name=users]').val(null).trigger('change');
                $(':input[name=assignable_groups]').val(null).trigger('change');
                $(':input[name=authoritative_group]').val(null).trigger('change');
                $(':input[name=role]').val(null).trigger('change');
                $(':input[name=compatible_roles]').val(null).trigger('change');
                $(':input[name=user_type]').val(null).trigger('change');
            } else {
                skip.portal = false;
            }
        });
    });

})(django.jQuery);
