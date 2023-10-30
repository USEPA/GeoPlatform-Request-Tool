(function ($) {

    $(document).ready(function () {
        let skip = true;
        // Bind on continent field change
        $(':input[name$=role]').on('change', function () {
            if (!skip) {


                // Get the field prefix, ie. if this comes from a formset form
                // var prefix = $(this).getFormPrefix();

                // Clear the autocomplete with the same prefix
                $(':input[name=authoritative_group]').val(null).trigger('change');
            } else {
                skip = false;
            }
        });
    });

})(django.jQuery);
