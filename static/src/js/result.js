function year_clicked(year_id) {
    console.log("year_clicked: "+year_id)
    $("#ue_section").load('/load_ue_section_by_year/'+year_id+'/0');
}

function show_result(year_id, session, ue_id) {
    console.log("show_result: "+year_id+', '+session+', ', ue_id)
    $("#result").css("display", "flex");
    $("#result_content").load('/show_result_content/'+year_id+'/'+session+'/'+ue_id+'/0');
}

function hide_content() {
    console.log('hide');
    $("#result").css("display", "none");
}

function search_ue_value(year_id) {
    ue_val = $("#input_search").val();
    $("#ue_section").load('/load_ue_section_by_year/'+year_id+'/'+ue_val);
}

function search_audit_value(year_id, session, ue_id) {
    num_audit_val = $("#input_search_num_audit").val();
    $("#result").css("display", "flex");
    $("#result_content").load('/show_result_content/'+year_id+'/'+session+'/'+ue_id+'/'+num_audit_val);
}