var initFormSets = function(options){
    $ = jQuery;
    // ----------------------------------------------- FormSet Initial -------------------------------------------------------//
    options.initialForms = {};
    options.totalForms = {};

    for (var index in options.prefixes){
        var formset_class = options.prefixes[index];
        options.initialForms[formset_class] = parseInt($('#id_'+formset_class+'_set-TOTAL_FORMS').val());
        options.totalForms[formset_class] = options.initialForms[formset_class];

        for (var field = 0; field < options.totalForms[formset_class]; field++){
           $('#id_'+ formset_class + '_set-' + field + '-DELETE, label[for="id_' + formset_class + '_set-' + field + '-DELETE"]').hide();
           $('#id_'+ formset_class + '_set-__prefix__-DELETE, label[for="id_' + formset_class + '_set-__prefix__-DELETE"]').hide();
        }

        if (options.totalForms[formset_class] <= 0){
            $('.removeForm[data-formset=' + formset_class + ']').hide();
        };
    };

    // ----------------------------------------------- FormSet Functions -----------------------------------------------//
    $('.addForm').on('click', function(){
        var formset = $(this).data('formset'); 
        addForm(formset);
    });
    $(document).on('click', '.removeForm', function(){
        var formset = $(this).data('formset'); 
        removeForm(formset, this);
    });

    function addForm(form_class){ 
        if (options.totalForms[form_class] < options.initialForms[form_class]){
            var fields = $('.' + form_class + '_row .wrapper').filter(':hidden').first();
            $('[id*="DELETE"]', fields).prop('checked', false);
            fields.show();
        } else {
            var fields = $('.'+form_class+'_row .wrapper').first().clone();
            fields.show();
            updateFieldsAttrs(fields, form_class);
            cleanFields(fields);
            $('.'+form_class+'_row').append(fields);        
        }
        options.totalForms[form_class] = options.totalForms[form_class] + 1;
        if (options.totalForms[form_class] > 0){
            $('.removeForm[data-formset=' + form_class + ']').show()
        }
    };

    function cleanFields(fields){
        $('select, input[type="url"], input[type="text"], textarea', fields).val('').trigger('change');
    }

    function updateFieldsAttrs(fields, form_class){
        $('[name^="' + form_class + '_set-"], [for^="id_' + form_class + '_set-"] ', fields).each(function(){
            if ($(this).attr('for') !== undefined){
                $(this).attr('for', updateAttrs($(this), 'for', form_class));
            } else{
                $(this).attr('name', updateAttrs($(this), 'name', form_class));
                $(this).attr('id', updateAttrs($(this), 'id', form_class));
            }
        });
    };

    function updateAttrs(field, attr, form_class){
        var field_attr = $(field).attr(attr).split('-');
        field_attr[1] = options.totalForms[form_class];
        return field_attr.join('-');
    };

    function removeForm(formset_prefix, element){
        var form_div = $(element).parents("div.wrapper");
        var delete_field = $('[id*="DELETE"]', form_div);
        var formset_class = $('.' + formset_prefix + '_row');
        var visible_divs = $("div.wrapper:not(:hidden)", formset_class);
        if (visible_divs.length === 1) cleanFields(form_div, formset_prefix);
        else {
            form_div.hide();
            delete_field.prop('checked', true);
        }
     };

    function validateEmptyFields(){
        for (var index in options.prefixes) {
            $('.wrapper').each(function(){
                var row_fields = $(this).find('input:not(:hidden), select');
                var hidden_fields = $(this).find('input:hidden');
    
                var map_empty = $.map(row_fields, function(elem){
                    return elem.value == ''
                });

                if (map_empty.every(elem => elem == true)){
                    $(hidden_fields).prop('checked', true);
                }
            });
        }
    };

    // ----------------------------------------------- Form Submition -----------------------------------------------//
    $('form').submit(function(event){
        validateEmptyFields();
        for (var index in options.prefixes){
            if (options.totalForms[options.prefixes[index]] < options.initialForms[options.prefixes[index]]){
                options.totalForms[options.prefixes[index]] = options.initialForms[options.prefixes[index]];
            }
            $('#id_'+options.prefixes[index]+'_set-TOTAL_FORMS').val(options.totalForms[options.prefixes[index]]);
        }
    });
}