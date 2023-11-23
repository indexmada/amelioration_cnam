function year_clicked(year_id) {
    $("#ue_section").load('/load_ue_section_by_year/'+year_id+'/0');
}

function show_result(year_id, session, ue_id) {
    $("#result").css("display", "flex");
    $("#result_content").load('/show_result_content/'+year_id+'/'+session+'/'+ue_id);
}

function hide_content() {
    console.log('hide');
    $("#result").css("display", "none");
}

function search_ue_value(year_id) {
    console.log('_______');
    ue_val = $("#input_search").val();
    $("#ue_section").load('/load_ue_section_by_year/'+year_id+'/'+ue_val);
}