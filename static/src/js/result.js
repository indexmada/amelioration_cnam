function year_clicked(year_id) {
    $("#ue_section").load('/load_ue_section_by_year/'+year_id);
}

function show_result(year_id, session, ue_id) {
    $("#result").css("display", "flex");
    $("#result_content").load('/show_result_content/'+year_id+'/'+session+'/'+ue_id);
}

function hide_content() {
    $("result").css("display", "none");
}