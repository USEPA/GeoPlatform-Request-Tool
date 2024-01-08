(function ($) {

    $(document).ready(function () {
        let skip = {role: true, portal: true};
        $(':input[name$=role]').on('change', function () {
            if (!skip.role) {
                $(':input[name=authoritative_group]').val(null).trigger('change');
            } else {
                skip.role = false;
            }
        });
        $(':input[name$=portal]').on('change', function () {
            if (!skip.portal) {
                $(':input[name=requester]').val(null).trigger('change');
                $(':input[name=users]').val(null).trigger('change');
                $(':input[name=assignable_groups]').val(null).trigger('change');
                $(':input[name=authoritative_group]').val(null).trigger('change');
                $(':input[name=role]').val(null).trigger('change');
            } else {
                skip.portal = false;
            }
        });
    });

})(django.jQuery);
